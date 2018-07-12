# Copyright 2008-2018 Univa Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable=no-self-use,no-name-in-module,no-member

import ipaddress
import itertools
import logging
import random
import re
import string
import threading
from typing import List, NoReturn, Optional

from sqlalchemy.orm.session import Session

from tortuga.db.models.hardwareProfile import HardwareProfile
from tortuga.db.models.network import Network
from tortuga.db.models.nic import Nic
from tortuga.db.models.node import Node
from tortuga.db.models.softwareProfile import SoftwareProfile
from tortuga.db.nodesDbHandler import NodesDbHandler
from tortuga.exceptions.invalidArgument import InvalidArgument
from tortuga.exceptions.invalidMacAddress import InvalidMacAddress
from tortuga.exceptions.macAddressAlreadyExists import MacAddressAlreadyExists
from tortuga.exceptions.networkNotFound import NetworkNotFound
from tortuga.exceptions.nicNotFound import NicNotFound
from tortuga.resourceAdapter.utility import get_provisioning_nics
from tortuga.utility.tortugaApi import TortugaApi


session_nodes_lock = threading.RLock()

session_nodes: List[Node] = []

# Maintain a list of used IP addresses. We do this to ensure we are
# not reusing IP addresses that were already used in this add nodes
# session.
reservedIps: List[str] = []

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class AddHostServerLocal(TortugaApi):
    def __init__(self):
        super(AddHostServerLocal, self).__init__()
        self._nodesDbHandler = NodesDbHandler()

    @staticmethod
    def clear_session_nodes(nodes: List[Node]) -> NoReturn:
        """Remove session entries for specified nodes"""

        with session_nodes_lock:
            for node in nodes:
                AddHostServerLocal.clear_session_node(node, lock=False)

    @staticmethod
    def clear_session_node(node: Node, lock: bool = True) -> NoReturn:
        if lock:
            session_nodes_lock.acquire()

        try:
            if not node.name:
                return

            hostname = get_host_name(node.name)

            logger.debug(
                'clear_session_node(): session_nodes=[{0}]'.format(
                    ' '.join([session_node
                              for session_node in session_nodes])))

            if hostname in session_nodes:
                logger.debug('DELETING session_nodes entry: {0}'.format(
                    hostname))

                session_nodes.remove(hostname)

            prov_nics = get_provisioning_nics(node)

            if prov_nics:
                if prov_nics[0].ip in reservedIps:
                    reservedIps.remove(prov_nics[0].ip)
        finally:
            if lock:
                session_nodes_lock.release()

    def initializeNode(self, session: Session, dbNode: Node,
                       dbHardwareProfile: HardwareProfile,
                       dbSoftwareProfile: SoftwareProfile,
                       nic_defs: List[dict],
                       bValidateIp: bool = True,
                       bGenerateIp: bool = True,
                       dns_zone: Optional[str] = None) -> NoReturn: \
            # pylint: disable=unused-argument
        """
        Assigns hostname and IP address, and inserts new record into
        Node table.

        Raises:
            InvalidArgument
            NodeAlreadyExists
        """

        # Do not attempt to validate IP addresses for hardware profiles
        # representing remote nodes.
        bValidateIp &= dbHardwareProfile.location != 'remote'

        if dbHardwareProfile.location != 'remote' and \
                not dbHardwareProfile.hardwareprofilenetworks:
            raise NetworkNotFound(
                'Hardware profile [{}] does not have a provisioning'
                ' network'.format(dbHardwareProfile.name))

        try:
            if not dbNode.name:
                # Generate unique name for new node
                dbNode.name = self.generate_node_name(
                    session, dbHardwareProfile.nameFormat,
                    rackNumber=dbNode.rack,
                    dns_zone=dns_zone)

            # Create NIC entries
            dbNode.nics = self._initializeNics(session, dbNode,
                                               dbHardwareProfile, nic_defs,
                                               bValidateIp=bValidateIp,
                                               bGenerateIp=bGenerateIp)

            self.getLogger().debug(
                'initializeNode(): initialized new node [%s]' % (
                    dbNode.name))
        except Exception:
            with session_nodes_lock:
                self.clear_session_node(dbNode)

            raise

    def generate_node_name(self, session: Session, nameFormat: str,
                           rackNumber: Optional[str] = None,
                           randomize: bool = False,
                           dns_zone: Optional[str] = None) -> str:
        '''
        Generate unique node name for the specified nameFormat.

        Raises:
            InvalidArgument
        '''

        try:
            base_name = nameFormat if rackNumber is None else \
                self._substituteHashSpecifier(
                    nameFormat, '#R', rackNumber)

            # Find all pre-existing nodes + nodes in the session
            if not randomize:
                nodes = self._nodesDbHandler.getNodesByNameFilter(
                    session,
                    self._substituteHashSpecifier(
                        base_name, '#N', '_'))

                # Get list of all existing nodes names
                node_names = [get_host_name(tmpNode.name)
                              for tmpNode in nodes]
            else:
                # Get all nodes matching name format WITH a random suffix
                nodes = self._nodesDbHandler.getNodesByNameFilter(
                    session,
                    self._substituteHashSpecifier(base_name, '#N', '_') +
                    '-_____')

                node_names = [
                    strip_random_node_name_suffix(get_host_name(node.name))
                    for node in nodes]

            with session_nodes_lock:
                # Build a list of all nodes in database and session
                if randomize:
                    all_session_nodes = node_names + \
                        strip_random_node_name_suffixes(session_nodes)
                else:
                    all_session_nodes = node_names + session_nodes

            for slot in itertools.count(1):
                name = self._substituteHashSpecifier(
                    base_name, '#N', slot)

                if name not in all_session_nodes:
                    break

            if randomize:
                # Add random 5 letter suffix to generated host name
                name += '-%s' % (
                    ''.join(random.sample(string.ascii_lowercase, 5)))

            with session_nodes_lock:
                # Add only host name to session_nodes cache
                session_nodes.append(name)

            return '{}.{}'.format(name, dns_zone) if dns_zone else name
        except InvalidArgument as exc:
            raise InvalidArgument('%s (format=[%s])' % (exc, nameFormat))

    def _substituteHashSpecifier(self, s, specifier, replacement):
        '''
        Replace the given specifier, '#R' or '#N', with the given
        replacement, which is either an integer (rack number or node
        number), or the string literal '_'.

        Don't touch this unless you're willing to rewrite it!

        Raises:
            InvalidArgument
        '''

        # Check arguments.

        if specifier != '#R' and specifier != '#N':
            raise InvalidArgument('specifier must be one of "#R" or "#N"')

        if isinstance(replacement, str):
            if replacement != '_':
                raise InvalidArgument(
                    'replacement must be "_" when type == str')
        elif not isinstance(replacement, int):
            raise InvalidArgument('replacement must an integer or "_"')

        # Point to the '#' (of '#R' or '#N') in the string.

        hashIdx = s.find(specifier)
        if hashIdx < 0:
            return s

        # Capture the portion to the left of the specifier.

        left = s[:hashIdx]

        # Point to the last 'R' or 'N' in the specifier.

        lastIdx = hashIdx + 1
        finalIdx = len(s) - 1
        while lastIdx < finalIdx and s[lastIdx + 1] == specifier[1]:
            lastIdx += 1

        # The width of the specifier (without the '#').

        width = lastIdx - hashIdx

        if replacement != '_' and replacement > (10 ** width - 1):
            raise InvalidArgument('Unable to generate unique host name')

        # Capture the portion to the right of the specifier.

        right = s[lastIdx + 1:]

        # Put it together.

        s = left

        if replacement == '_':
            s += '_' * width
        else:
            s += '%0*d' % (width, replacement)

        s += right

        return s

    def _initializeNics(self, session: Session, dbNode: Node,
                        dbHardwareProfile: HardwareProfile,
                        nic_defs: List[dict], bValidateIp: bool = True,
                        bGenerateIp: bool = True) -> List[Nic]:
        """
        Return list of Nic objects reflecting the configuration of dbNode
        and nic definitions provided in nic_defs.

        :raises NetaNotFound:
        :raises InvalidMacAddress:
        :raises MacAddressAlreadyExists:

        """
        nics = []

        hwpnetworks = dbHardwareProfile.hardwareprofilenetworks[:]

        hwpnetworks.sort(key=lambda a: a.networkdevice.name)

        for nic_def, dbHardwareProfileNetwork in itertools.zip_longest(
                nic_defs, hwpnetworks, fillvalue=None):
            # Create a nic for each associated hardware profile network
            dbNic = Nic()

            dbNic.node = dbNode

            if nic_def and 'mac' in nic_def:
                #
                # MAC addresses are generated for virtualization platforms
                # such as libvirt and VMware
                #
                dbNic.mac = self._validate_mac_address(
                    session, nic_def['mac'], dbHardwareProfileNetwork.network)

            #
            # Validate IP, if specified, otherwise generate an IP, if
            # requested
            #
            if nic_def and 'ip' in nic_def:
                if bValidateIp:
                    self._validate_ip_address(
                        nic_def['ip'], dbHardwareProfileNetwork.network)

                dbNic.ip = nic_def['ip']
            else:
                if dbHardwareProfile.location == 'local' and \
                        not dbHardwareProfileNetwork:
                    raise NicNotFound(
                        'Hardware profile [%s] does not have a provisioning'
                        ' network' % (dbHardwareProfile.name))

                if bGenerateIp and \
                        dbHardwareProfileNetwork.network.type == 'provision':
                    # Generate an IP address for the specified nic
                    dbNic.ip = self.generate_provisioning_ip_address(
                        dbHardwareProfileNetwork.network)

                    self.getLogger().debug(
                        'Generated IP [%s] for node [%s]' % (
                            dbNic.ip, dbNode.name))

            if dbNic.ip or \
                    dbHardwareProfileNetwork and \
                    dbHardwareProfileNetwork.network.type != 'provision':
                # Only add a network and network device for nodes that have
                # managed IP addresses.

                if dbHardwareProfileNetwork:
                    dbNic.network = dbHardwareProfileNetwork.network
                    dbNic.networkdevice = \
                        dbHardwareProfileNetwork.networkdevice

            # Set the 'boot' flag if this is a provisioning network
            dbNic.boot = dbNic.network and dbNic.network.type == 'provision'

            if dbNic.ip:
                reservedIps.append(dbNic.ip)

            nics.append(dbNic)

        return nics

    def _validate_mac_address(self, session: Session, mac_address: str,
                              network: Network) -> str:
        """
        Validate a MAC address and make sure it is not a duplicate.

        :raises InvalidMacAddress:
        :raises MacAddressAlreadyExists:

        """

        if not mac_address:
            raise InvalidMacAddress('MAC address is empty/undefined')

        #
        # Normalize and Validate MAC address formatting
        #
        mac_regex = re.compile(
            r'^([0-9A-Fa-f]{2}[:-]?){5}[0-9A-Fa-f]{2}([:-]?.*)?$')
        if not mac_regex.match(mac_address):
            raise InvalidMacAddress(
                'MAC address [{}] is invalid/malformed'.format(mac_address))

        if '-' in mac_address:
            mac_address = mac_address.replace('-', ':').lower()

        if ':' not in mac_address:
            mac_address = '{}:{}:{}:{}:{}:{}'.format(mac_address[0:2],
                                                     mac_address[2:4],
                                                     mac_address[4:6],
                                                     mac_address[6:8],
                                                     mac_address[8:10],
                                                     mac_address[10:12])

        #
        # Make sure that the MAC address does not already exist on the
        # same provisioning network
        #
        db_host_list = self._nodesDbHandler.getNodesByMac(session,
                                                          [mac_address])
        for db_host in db_host_list:
            for db_nic in db_host.nics:
                if db_nic.mac == mac_address and \
                        db_nic.networkId == network.id:
                    raise MacAddressAlreadyExists(
                        'The MAC address [{}] already exists '
                        'on the network [{}/{}]'.format(mac_address,
                                                        network.address,
                                                        network.netmask)
                    )

        return mac_address

    def _validate_ip_address(self, ip, network) -> NoReturn:
        """
        :raises NetworkNotFound:

        """
        #
        # Only validate IP addresses in 'local' hardware profiles
        #
        try:
            requested_ip = ipaddress.IPv4Address(str(ip))

            provisioning_network = ipaddress.IPv4Network(
                '{}/{}'.format(network.address, network.netmask))

            if requested_ip not in provisioning_network:
                raise NetworkNotFound(
                    'IP address [{}] not on network [{}]'.format(
                        ip, provisioning_network))
        except ipaddress.AddressValueError:
            #
            # malformed ip address
            #
            raise NetworkNotFound('IP address [{}] is invalid'.format(ip))

    def generate_provisioning_ip_address(self, network):
        """
        Raises:
            InvalidArgument
        """

        if not network or network.usingDhcp:
            # This hardwareProfile uses an external DHCP server
            # (we do not assign the IP address for this hardwareProfile.)
            return None

        n = ipaddress.IPv4Network(
            '%s/%s' % (network.address, network.netmask))

        # Get list of all currently allocated IPs on this network
        ips = [
            ipaddress.IPv4Address(str(dbNic.ip))
            for dbNic in network.nics if dbNic and dbNic.ip]

        with session_nodes_lock:
            # Include reserved IPs
            ips.extend([ipaddress.IPv4Address(str(ip))
                        for ip in reservedIps])

            if not network.startIp:
                # Assume the starting IP address is the first IP address in
                # the subnet
                try:
                    ip = n[1]
                except IndexError:
                    raise InvalidArgument('IP address space exhausted')
            else:
                ip = ipaddress.IPv4Address(str(network.startIp))

            # Ensure there's a valid increment if none is defined in the
            # network object.
            inc = network.increment if network.increment else 1

            for _ in range(n.num_addresses):
                if ip not in ips:
                    # Found available IP address within address space
                    break

                ip += int(inc)
            else:
                raise InvalidArgument('IP address space exhausted')

            if ip == n.broadcast_address:
                raise InvalidArgument('IP address space exhausted')

            reservedIps.append(ip.exploded)

        self.getLogger().debug(
            'Assigning IP address [%s] on network [%s]' % (
                ip.exploded, str(n)))

        return ip.exploded


def strip_random_node_name_suffix(name):
    # Strip leading dash ("-") and 5 random character node name suffix
    return name[:-6]


def strip_random_node_name_suffixes(names):
    return [strip_random_node_name_suffix(name) for name in names]


def get_host_name(name):
    # Extract host name component from FQDN
    return name.split('.', 1)[0]
