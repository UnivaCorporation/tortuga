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

import sys
from typing import Optional

from sqlalchemy.orm.session import Session

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.cli.utils import parse_tags
from tortuga.db.dbManager import DbManager
from tortuga.db.hardwareProfileDbApi import HardwareProfileDbApi
from tortuga.db.nodeDbApi import NodeDbApi
from tortuga.db.softwareProfileDbApi import SoftwareProfileDbApi


class UctagCli(TortugaCli):
    def __init__(self, *args, **kwargs):
        self._hwp_api = HardwareProfileDbApi()
        self._node_api = NodeDbApi()
        self._swp_api = SoftwareProfileDbApi()
        super().__init__(*args, **kwargs)

    def parseArgs(self, usage: Optional[str] = None):
        subparsers = self.getParser().add_subparsers(help='sub-command help',
                                                     dest='subparser_name')

        add_subparser = subparsers.add_parser('add')
        add_subparser.add_argument('--node', dest='nodespec')
        add_subparser.add_argument('--software-profile', metavar='NAME')
        add_subparser.add_argument('--hardware-profile', metavar='NAME')
        add_subparser.add_argument('--tags', action='append', dest='tags',
                                   metavar='key=value[,key=value]')
        add_subparser.set_defaults(func=self.add_tag)

        remove_subparser = subparsers.add_parser('remove')
        remove_subparser.add_argument('--node', dest='nodespec')
        remove_subparser.add_argument('--software-profile', metavar='NAME')
        remove_subparser.add_argument('--hardware-profile', metavar='NAME')
        remove_subparser.add_argument('--tags', action='append', dest='tags',
                                      metavar='key[,key]')
        remove_subparser.set_defaults(func=self.remove_tag)

        list_subparser = subparsers.add_parser('list')
        list_subparser.add_argument('--all-resources', action='store_true')
        list_subparser.add_argument('--nodes', action='store_true')
        list_subparser.add_argument('--software-profiles',
                                    action='store_true')
        list_subparser.add_argument('--hardware-profiles',
                                    action='store_true')
        list_subparser.set_defaults(func=self.list_tag)

        return super().parseArgs(usage=usage)

    def runCommand(self):
        args = self.parseArgs()

        with DbManager().session() as session:
            args.func(session, args)

    def add_tag(self, session: Session, args):
        if not args.nodespec and not args.software_profile and \
                not args.hardware_profile:
            sys.stderr.write('Error: must specify --nodes'
                             '/--software-profile/--hardware-profile\n')
            sys.stderr.flush()
            sys.exit(1)

        tags = parse_tags(args.tags)

        if args.nodespec:
            nodes = self._node_api.getNodesByNameFilter(session,
                                                        args.nodespec)
            for node in nodes:
                node_tags = node.getTags()
                node_tags.update(tags)
                self._node_api.set_tags(session, node_id=node.getId(),
                                        tags=node_tags)
                print(node.getName(), node.getTags())

        if args.software_profile:
            for name in args.software_profile.split(','):
                swp = self._swp_api.getSoftwareProfile(session, name)
                swp_tags = swp.getTags()
                swp_tags.update(tags)
                swp.setTags(swp_tags)
                self._swp_api.updateSoftwareProfile(session, swp)

        if args.hardware_profile:
            for name in args.hardware_profile.split(','):
                hwp = self._hwp_api.getHardwareProfile(session, name)
                hwp_tags = hwp.getTags()
                hwp_tags.update(tags)
                hwp.setTags(hwp_tags)
                self._hwp_api.updateHardwareProfile(session, hwp)

        session.commit()

    def remove_tag(self, session: Session, args):
        if not args.nodespec and not args.software_profile and \
                not args.hardware_profile:
            sys.stderr.write('Error: must specify --nodes'
                             '/--software-profile/--hardware-profile\n')
            sys.stderr.flush()
            sys.exit(1)

        tag_keys = []
        for tag_string in args.tags:
            tag_keys.extend(tag_string.split(','))

        if args.nodespec:
            nodes = self._node_api.getNodesByNameFilter(session,
                                                        args.nodespec)
            for node in nodes:
                node_tags = node.getTags()
                for key in tag_keys:
                    if key in node_tags.keys():
                        node_tags.pop(key)
                self._node_api.set_tags(session, node_id=node.getId(),
                                        tags=node_tags)
                print(node.getName(), node.getTags())

        if args.software_profile:
            for name in args.software_profile.split(','):
                swp = self._swp_api.getSoftwareProfile(session, name)
                swp_tags = swp.getTags()
                for key in tag_keys:
                    if key in swp_tags.keys():
                        swp_tags.pop(key)
                swp.setTags(swp_tags)
                self._swp_api.updateSoftwareProfile(session, swp)

        if args.hardware_profile:
            for name in args.hardware_profile.split(','):
                hwp = self._hwp_api.getHardwareProfile(session, name)
                hwp_tags = hwp.getTags()
                for key in tag_keys:
                    if key in hwp_tags.keys():
                        hwp_tags.pop(key)
                hwp.setTags(hwp_tags)
                self._hwp_api.updateHardwareProfile(session, hwp)

        session.commit()

    def list_tag(self, session: Session, args):
        report = TagReport()

        if args.all_resources or args.nodes:
            for node in self._node_api.getNodeList(session):
                for key, value in node.getTags().items():
                    report.add_node(key, value, node)
        
        if args.all_resources or args.software_profiles:
            for swp in self._swp_api.getSoftwareProfileList(session):
                for key, value in swp.getTags().items():
                    report.add_swp(key, value, swp)
        
        if args.all_resources or args.hardware_profiles:
            for hwp in self._hwp_api.getHardwareProfileList(session):
                for key, value in hwp.getTags().items():
                    report.add_hwp(key, value, hwp)

        for key, values in report.keys.items():
            for value, types in values.items():
                print('{} = {}:'.format(key, value))
                for type_, names in types.items():
                    print('  {}:'.format(type_))
                    for name in names:
                        print('    - {}'.format(name))


class TagReport:
    def __init__(self):
        self.keys = {}
    
    def _make_hier(self, key, value, type_):
        if key not in self.keys.keys():
            self.keys[key] = {}
        if value not in self.keys[key]:
            self.keys[key][value] = {}
        if type_ not in self.keys[key][value]:
            self.keys[key][value][type_] = []
    
    def add_node(self, key, value, node):
        self._make_hier(key, value, 'nodes')
        self.keys[key][value]['nodes'].append(node.getName())
    
    def add_swp(self, key, value, swp):
        self._make_hier(key, value, 'software profiles')
        self.keys[key][value]['software profiles'].append(swp.getName())
    
    def add_hwp(self, key: str, value: str, hwp):
        self._make_hier(key, value, 'hardware profiles')
        self.keys[key][value]['hardware profiles'].append(hwp.getName())


def main():
    UctagCli().run()
