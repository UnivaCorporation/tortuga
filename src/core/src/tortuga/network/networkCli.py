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

# pylint: disable=no-member,maybe-no-member

import ipaddress

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.exceptions.invalidCliRequest import InvalidCliRequest
from tortuga.wsapi.networkWsApi import NetworkWsApi


class NetworkCli(TortugaCli):
    """
    Base network command line interface class.
    """

    def __init__(self):
        super(NetworkCli, self).__init__()

        # Initialize api instance
        self._networkApi = None

    def setupDefaultOptions(self):
        """
        Set up default command-line options for all attributes in network...
        used by update and add operations
        """

        cmdline_grpname = _('Command-line')
        self.addOptionGroup(cmdline_grpname, None)

        # Simple common Options
        self.addOptionToGroup(cmdline_grpname, '--network',
                              help=_('Network in XXX.XXX.XXX.XXX/YY or'
                                     ' XXX.XXX.XXX.XXX/YYY.YYY.YYY.YYY'
                                     ' format'))

        self.addOptionToGroup(cmdline_grpname, '--address', dest='address',
                              help=_('Network address'))

        self.addOptionToGroup(cmdline_grpname, '--netmask', dest='netmask',
                              help=_('Network mask'))

        self.addOptionToGroup(cmdline_grpname, '--suffix', dest='suffix',
                              help=_('Network suffix'))

        self.addOptionToGroup(cmdline_grpname, '--gateway', dest='gateway',
                              help=_('Network gateway'))

        self.addOptionToGroup(cmdline_grpname, '--options', dest='options',
                              help=_('Network options'))

        self.addOptionToGroup(cmdline_grpname, '--name', dest='name',
                              help=_('Network name'))

        self.addOptionToGroup(cmdline_grpname, '--start-ip', dest='startIp',
                              help=_('Network starting IP address'))

        self.addOptionToGroup(cmdline_grpname, '--type', dest='type',
                              help=_('Network type'))

        self.addOptionToGroup(cmdline_grpname, '--increment',
                              dest='increment',
                              help=_('Network increment'), type=int)

        self.addOptionToGroup(cmdline_grpname,
                              '--dhcp', dest='usingDhcp',
                              action='store_true',
                              help=_('Network addresses assigned via DHCP'))

        self.addOptionToGroup(cmdline_grpname, '--static', dest='usingDhcp',
                              action='store_false',
                              help=_('Network addresses assigned'
                                     ' statically'))

        self.addOptionToGroup(cmdline_grpname, '--vlan-id', dest='vlanId',
                              help=_('VLAN ID.'))

        self.addOptionToGroup(cmdline_grpname, '--vlan-parent-network',
                              dest='vlanParentNetwork',
                              help=_('Parent network of the VLAN network'))

        # Or an xml file can be passed in
        xml_grpname = _('From XML file')
        self.addOptionGroup(xml_grpname, None)

        self.addOptionToGroup(xml_grpname, '--xml-file', dest='xmlFile',
                              help=_('XML file containing network'
                                     ' definition'))

    def assertIp(self, ip, parameterName, errorMsg=None): \
            # pylint: disable=no-self-use
        """
        Convienience function for testing IPs and raising a configurable
        exception if the IP is invalid.
        """

        if errorMsg is None:
            errorMsg = _('The %s parameter must be a valid IP address.') % (
                parameterName)

        try:
            ipaddress.IPv4Address(str(ip))
        except ipaddress.AddressValueError:
            raise InvalidCliRequest(errorMsg)

    def updateNetwork(self, network):
        """
        Update a passed in network tortuga object with the values passed
        in on the command line.
        """

        # Check for conflicting command-line options
        if (self.getArgs().netmask or self.getArgs().address) and \
                self.getArgs().network:
            self.getParser().error(
                'Specify network using --network/--netmask or --network')

        if self.getArgs().network:
            # Use 'ipaddr' module to validate network spec
            parsed_network, parsed_netmask = \
                self.parseNetworkParameter(self.getArgs().network)

            network.setAddress(parsed_network)
            network.setNetmask(parsed_netmask)
        else:
            if self.getArgs().address is not None:
                self.assertIp(self.getArgs().address, '--address')
                network.setAddress(self.getArgs().address)

            if self.getArgs().netmask is not None:
                self.assertIp(self.getArgs().netmask, '--netmask')
                network.setNetmask(self.getArgs().netmask)

        if self.getArgs().suffix is not None:
            network.setSuffix(self.getArgs().suffix)

        if self.getArgs().gateway is not None:
            self.assertIp(self.getArgs().gateway, '--gateway')
            network.setGateway(self.getArgs().gateway)

        if self.getArgs().name is not None:
            network.setName(self.getArgs().name)

        if self.getArgs().startIp is not None:
            self.assertIp(self.getArgs().startIp, '--start-ip')
            network.setStartIp(self.getArgs().startIp)

        if self.getArgs().type is not None:
            network.setType(self.getArgs().type)

        if self.getArgs().increment is not None:
            network.setIncrement(self.getArgs().increment)

        optionsString = network.getArgs()
        optionsDict = {}
        if optionsString:
            # VLAN info may already exist for this network
            optionsList = optionsString.split(';')
            for originalOption in optionsList:
                key, value = originalOption.split('=')
                optionsDict[key] = value

        vlanIdFound = self.getArgs().vlanId is not None or \
            'vlan' in optionsDict

        vlanParentNetworkFound = self.\
            _options.vlanParentNetwork is not None or \
            'vlanparent' in optionsDict

        if (vlanIdFound and not vlanParentNetworkFound) or \
                (not vlanIdFound and vlanParentNetworkFound):
            raise InvalidCliRequest(
                _('--vlan-id and --vlan-parent-network must be used'
                  ' together.'))

        if self.getArgs().vlanId:
            optionsDict['vlan'] = self.getArgs().vlanId

        if self.getArgs().vlanParentNetwork:
            # Match the given parent network to a network in the DB
            networkAddr, subnetMask = self.parseNetworkParameter(
                self.getArgs().vlanParentNetwork)

            existingNetworkList = self.getNetworkApi().getNetworkList()

            matchingNetworkId = None

            for existingNetwork in existingNetworkList:
                if existingNetwork.getAddress() == networkAddr and \
                        existingNetwork.getNetmask() == subnetMask:
                    matchingNetworkId = existingNetwork.getId()

            if not matchingNetworkId:
                raise InvalidCliRequest(
                    _('Network [%s] not found') % (
                        self.getArgs().vlanParentNetwork))

            optionsDict['vlanparent'] = matchingNetworkId

        newOptions = ''

        if self.getArgs().vlanId or self.getArgs().vlanParentNetwork:
            for entry in list(optionsDict.items()):
                optionKey, optionValue = entry
                newOptions += '%s=%s;' % (optionKey, optionValue)

            # Take off the last semicolon
            newOptions = newOptions[:-1]

        if self.getArgs().options:
            if newOptions:
                newOptions = '%s;%s' % (newOptions, self.getArgs().options)
            else:
                newOptions = self.getArgs().options

        if self.getArgs().options or self.getArgs().vlanId or \
                self.getArgs().vlanParentNetwork:
            network.setOptions(newOptions)

        if self.getArgs().usingDhcp is not None:
            network.setUsingDhcp(self.getArgs().usingDhcp)

    def getNetworkFromXml(self):
        """
        If the xmlFile option is present attempt to create a Network
        object from the xml.  Otherwise return None
        """

        network = None

        if self.getArgs().xmlFile:
            # An XML file was provided as input...start with that...
            f = open(self.getArgs().xmlFile, 'r')

            try:
                xmlString = f.read()
            finally:
                f.close()

            try:
                from tortuga.objects.network import Network
                network = Network.getFromXml(xmlString)
            except Exception as ex:   # pylint: disable=W0703
                self.getLogger().debug('Error parsing xml %s' % ex)

            if network is None:
                raise InvalidCliRequest(
                    _('File [%s] does not contain a valid network.') % (
                        self.getArgs().xmlFile))

        return network

    def getNetworkApi(self):
        """
        Caching method for getting a networkApi instance.

        """
        if self._networkApi is None:
            self._networkApi = NetworkWsApi(self.getUsername(),
                                            self.getPassword(),
                                            baseurl=self.getUrl())
        return self._networkApi

    def parseNetworkParameter(self, network): \
            # pylint: disable=no-self-use
        """
        Validator for the --network parameter.
        """

        try:
            result = ipaddress.IPv4Network(str(network))
        except ipaddress.AddressValueError:
            # Invalid argument to --network specified
            raise InvalidCliRequest(
                _('--network argument must be formatted as '
                  ' XXX.XXX.XXX.XXX/YY or XXX.XXX.XXX.XXX/YYY.YYY.YYY.YYY'))

        return result.network_address.exploded, result.netmask.exploded

    def validateNetwork(self, network):     # pylint: disable=no-self-use
        """
        Verify a network object has the minimum populated fields needed to
        add it to the database
        """

        if not network.getAddress():
            raise InvalidCliRequest(_('Network address must be specified.'))

        if not network.getNetmask():
            raise InvalidCliRequest(_('Subnet mask must be specified.'))

        if not network.getType():
            raise InvalidCliRequest(_('Network type must be specified.'))

        if network.getUsingDhcp() is None:
            raise InvalidCliRequest(
                _('Address allocation must be specified as DHCP or'
                  ' static.'))

        if network.getIncrement():
            increment = network.getIncrement()
            try:
                value = int(increment)
                if value < 1:
                    raise InvalidCliRequest(
                        _('Increment must be positive.'))
            except ValueError:
                raise InvalidCliRequest(
                    _('Increment must be a positive integer.'))

    def get_network_from_cmdline(self, retrieve_network=True):
        """
        If 'retrieve_network' is True, return Network object matching network
        specification (either --address/--netmask or --network), otherwise
        return None.

        Raises:
            NetworkNotFound
        """

        # Get network from XML if an xml file was passed in
        network = self.getNetworkFromXml()
        if network:
            return network

        # If we didn't have xml but network load the network from the
        # api...otherwise error

        if self.getArgs().address is None and \
                self.getArgs().network is None or \
                ((self.getArgs().address or self.getArgs().netmask) and
                 self.getArgs().network):
            self.getParser().error(
                '--address/--netmask OR --network must be specified')

        if self.getArgs().network:
            _network, _netmask = self.parseNetworkParameter(
                self.getArgs().network)
        else:
            _network = self.getArgs().address
            _netmask = self.getArgs().netmask

            if _netmask is None:
                self.getParser().error('--netmask must be specified')

        if not retrieve_network:
            return None

        return self.getNetworkApi().getNetwork(_network, _netmask)
