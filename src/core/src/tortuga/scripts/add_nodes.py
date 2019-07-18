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
#######################################################################

# pylint: disable=no-member

import argparse
import ipaddress
import itertools
import os.path
import sys

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.cli.utils import parse_tags
from tortuga.exceptions.httpErrorException import HttpErrorException
from tortuga.exceptions.urlErrorException import UrlErrorException
from tortuga.wsapi.addHostWsApi import AddHostWsApi


class AddNodes(TortugaCli): \
        # pylint: disable=too-few-public-methods
    def parseArgs(self, usage=None):
        mainGroup = _('Main Options')
        self.addOptionGroup(mainGroup, None)

        # Do not set any defaults through the options!

        self.addOptionToGroup(
            mainGroup, '--hardware-profile',
            metavar='NAME',
            dest='hardwareProfileName',
            help=_('Add nodes based on this hardware profile.'))

        self.addOptionToGroup(
            mainGroup, '--extra-arg', '-e',
            dest='extra_args', metavar="<key|key=value>",
            action='append',
            help=_('Pass extra arguments to resource adapter.'))

        self.addOptionToGroup(
            mainGroup, '--tags',
            dest='tags', metavar='key=value[,key=value]',
            action='append',
            help='Key-value pairs associated with new node(s)')

        self.addOptionToGroup(
            mainGroup, '--rack',
            dest='rackNumber',
            type=int,
            help=_('Value for "#RR" in hardware profile name format.'))

        self.addOptionToGroup(
            mainGroup, '--software-profile',
            metavar='NAME',
            dest='softwareProfileName',
            help=_('Associate new node(s) with given software profile.'))

        self.addOptionToGroup(
            mainGroup, '--force', action='store_true', default=False,
            help=_('Allow addition of nodes to soft locked software profile.')
        )

        # This is a deprecated argument (replaced with '--count')
        self.addOptionToGroup(
            mainGroup, '--node-count',
            dest='nodeCount',
            help=argparse.SUPPRESS,
            type=int)

        self.addOptionToGroup(
            mainGroup, '-n', '--count',
            dest='nodeCount', metavar='COUNT',
            help=_('Specify number of nodes to add.'),
            type=int)

        self.addOptionToGroup(
            mainGroup, '--resource-adapter-configuration', '-A',
            metavar='NAME',
            help=_('Specify resource adapter configuration for operation'))

        self.addOptionToGroup(
            mainGroup, '--data',
            metavar="<user1:module:path1:dest_root_path1;user2:module:path2:dest_root_path2>;...>",
            dest='data',
            help=_('Add user data sets.'))

        outputGroup = _('Output options')
        self.addOptionGroup(outputGroup, None)

        self.addOptionToGroup(
            outputGroup,
            '--quiet',
            action='store_true',
            default=False,
            help=_('Display only node request id (suitable for scripting)'))

        macGroup = _('Single Node Import Options')
        self.addOptionGroup(macGroup, None)

        self.addOptionToGroup(
            macGroup, '--mac-addr',
            dest='macAddr',
            help=_('MAC address to be added to cluster'))

        self.addOptionToGroup(
            macGroup, '--host-name',
            dest='hostName',
            help=_('Set the host name for the node being imported'))

        self.addOptionToGroup(
            macGroup, '--ip-address',
            dest='ipAddress',
            help=_('Set the IP address for the node being imported'))

        macFileImportGroup = _('File Import Options')
        self.addOptionGroup(macFileImportGroup, None)

        self.addOptionToGroup(
            macFileImportGroup, '--mac-file',
            dest='macImportFile',
            metavar='FILE',
            help=_('File containing list of MAC addresses to be added'
                   ' to cluster'))

        super(AddNodes, self).parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs()

        # Validate options
        if self.getArgs().macImportFile:
            if self.getArgs().nodeCount:
                sys.stderr.write('Ignoring \'--count\' option when importing'
                                 ' from MAC file\n')

        addHostWsApi = self.configureClient(AddHostWsApi)

        addNodesRequest = {
            'force': self.getArgs().force,
        }

        if self.getArgs().hardwareProfileName:
            addNodesRequest['hardwareProfile'] = \
                self.getArgs().hardwareProfileName

        # Parse extra arguments
        extra_args = dict()

        for extra_arg in self.getArgs().extra_args or []:
            key, value = extra_arg.split('=', 1) \
                if '=' in extra_arg else (extra_arg, None)

            extra_args[key] = value

        if self.getArgs().extra_args and extra_args:
            addNodesRequest['extra_args'] = extra_args

        if not self.getArgs().macImportFile and \
                self.getArgs().nodeCount is not None:
            # Only set the node count if not importing from a file
            addNodesRequest['count'] = self.getArgs().nodeCount

        if self.getArgs().rackNumber is not None:
            addNodesRequest['rack'] = self.getArgs().rackNumber

        if self.getArgs().softwareProfileName:
            addNodesRequest['softwareProfile'] = \
                self.getArgs().softwareProfileName

        if not self.getArgs().hardwareProfileName and \
                not self.getArgs().softwareProfileName:
            self.getParser().error(
                '--software-profile or --hardware-profile and '
                ' --software-profile must be specified'
            )

        if self.getArgs().tags:
            addNodesRequest['tags'] = parse_tags(self.getArgs().tags)

        if self.getArgs().data:
            addNodesRequest['data'] = self.getArgs().data

        nodeDetails = []

        if self.getArgs().macAddr or self.getArgs().ipAddress or \
                self.getArgs().hostName:
            if self.getArgs().nodeCount is not None:
                addNodesRequest['count'] = self.getArgs().nodeCount

            nics = self.__extract_nics(
                self.getArgs().ipAddress,
                self.getArgs().macAddr.lower()
                if self.getArgs().macAddr else None)

            nodeDetail = {}

            if nics:
                nodeDetail['nics'] = nics

                addNodesRequest['count'] = 1

            if self.getArgs().hostName:
                nodeDetail['name'] = self.getArgs().hostName

                addNodesRequest['count'] = 1

            nodeDetails.append(nodeDetail)
        else:
            if self.getArgs().macImportFile:
                if not os.path.exists(self.getArgs().macImportFile):
                    sys.stderr.write(
                        _('Error: file [%s] not found') % (
                            self.getArgs().macImportFile) + '\n')

                    raise SystemExit(1)

                # Parse input file
                with open(self.getArgs().macImportFile) as fd:
                    for line in fd.readlines():
                        if not line == '' and not line[0] == '#':
                            itemList = line.rstrip().split()
                            mac = ipAddr = hostname = None
                            for item in itemList:
                                # Definatly MAC
                                if not item.find(':') < 0:
                                    mac = item.lower()
                                # IP or hostname
                                elif not item.find('.') < 0:
                                    try:
                                        ipAddr = str(ipaddress.IPv4Address(item))
                                    except ipaddress.AddressValueError:
                                        # Unable to convert to dotted quad;
                                        # must be a host name
                                        hostname = item
                                else:
                                    hostname = item

                            nodeDetail = {}

                            if mac:
                                nodeDetail['mac'] = mac

                            if ipAddr:
                                nodeDetail['ip'] = ipAddr

                            if hostname:
                                nodeDetail['name'] = hostname

                            nodeDetails.append({'nics': [nodeDetail]})

        if nodeDetails:
            addNodesRequest['nodeDetails'] = nodeDetails

            if 'count' not in addNodesRequest:
                addNodesRequest['count'] = len(nodeDetails)

        if self.getArgs().resource_adapter_configuration:
            addNodesRequest['resource_adapter_configuration'] = \
                self.getArgs().resource_adapter_configuration

        try:
            addHostSession = addHostWsApi.addNodes(addNodesRequest)

            if self.getArgs().quiet:
                sys.stdout.write('{0}\n'.format(addHostSession))
            else:
                # Async (default) invocation; show user output
                sys.stdout.write(
                    'Add host session [{0}] created successfully.\n'
                    ' Use \'get-node-requests -r {0}\' to query request'
                    ' status\n'.format(addHostSession))

                sys.stdout.flush()
        except (UrlErrorException, HttpErrorException):
            sys.stderr.write(
                'Error: unable to communicate with Tortuga webservice.\n'
                '\nEnsure webservice is running. Check log(s)'
                ' for additional information.\n')

            raise SystemExit(1)

    def __extract_nics(self, ipAddrSpec, macAddrSpec): \
            # pylint: disable=no-self-use
        """macAddrSpec can be a list of MAC addresses in the following
        format:

        ##:##:##:##:##:##
        ##:##:##:##:##:##/devname
        ##:##:##:##:##:##,##:##:##:##:##:##[,[...]]
        ##:##:##:##:##:##/devname,##:##:##:##:##:##/devname[,[...]]

        """

        ipAddrList = ipAddrSpec.split(',') if ipAddrSpec else []
        macAddrList = macAddrSpec.lower().split(',') if macAddrSpec else []

        nics = []

        # Zip list of IP addresses with MAC spec list
        for ipAddr, macSpec in itertools.zip_longest(
                ipAddrList, macAddrList, fillvalue=''):
            nic_def = {}

            # Either ipAddr or macSpec can be empty; do not attempt to
            # parse or add values to dict if empty/undefined.
            if '/' in macSpec:
                nic_def['mac'], nic_def['device'] = macSpec.lower().split('/')
            elif macSpec:
                nic_def['mac'] = macSpec.lower()

            if ipAddr:
                nic_def['ip'] = ipAddr

            nics.append(nic_def)

        return nics


def main():
    AddNodes().run()
