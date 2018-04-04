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
import argparse
from tortuga.db.dbManager import DbManager
from tortuga.db.nodesDbHandler import NodesDbHandler
from tortuga.db.softwareProfilesDbHandler import SoftwareProfilesDbHandler
from tortuga.db.hardwareProfilesDbHandler import HardwareProfilesDbHandler
from tortuga.db.tags import Tags
from tortuga.db.tagsDbHandler import TagsDbHandler
from tortuga.cli.tortugaCli import TortugaCli


class UctagCli(TortugaCli):
    def runCommand(self):
        parser = argparse.ArgumentParser()

        subparsers = parser.add_subparsers(help='sub-command help',
                                           dest='subparser_name')

        add_subparser = subparsers.add_parser('add')
        add_subparser.add_argument('--node', dest='nodespec')
        add_subparser.add_argument('--software-profile', metavar='NAME')
        add_subparser.add_argument('--hardware-profile', metavar='NAME')
        add_subparser.add_argument('--tag', action='append', dest='tags',
                                   type=key_value_pair)
        add_subparser.set_defaults(func=self.add_tag)

        remove_subparser = subparsers.add_parser('remove')
        remove_subparser.add_argument('--node', dest='nodespec')
        remove_subparser.add_argument('--tag', action='append', dest='tags',
                                      type=key_value_pair)
        remove_subparser.set_defaults(func=self.remove_tag)

        delete_subparser = subparsers.add_parser('delete')
        delete_subparser.add_argument('--force', action='store_true',
                                      default=False)
        delete_subparser.add_argument('--tag', action='append', dest='tags')
        delete_subparser.set_defaults(func=self.delete_tag)

        # 'list' action
        list_subparser = subparsers.add_parser('list')
        list_subparser.add_argument('--all-resources', action='store_true')
        list_subparser.add_argument('--nodes', action='store_true')
        list_subparser.add_argument('--software-profiles', action='store_true')
        list_subparser.add_argument('--hardware-profiles', action='store_true')
        list_subparser.set_defaults(func=self.list_tag)

        args = parser.parse_args()

        args.func(args)

    def add_tag(self, args):
        """Handle 'add' action - associate tag(s) with resources"""

        if not args.nodespec and not args.software_profile and \
                not args.hardware_profile:
            sys.stderr.write('Error: must specify --nodes'
                             '/--software-profile/--hardware-profile\n')
            sys.stderr.flush()
            sys.exit(1)

        session = DbManager().openSession()

        try:
            nodes = []
            softwareprofiles = []
            hardwareprofiles = []

            if args.nodespec:
                nodespec = args.nodespec.replace('*', '%')

                nodes = NodesDbHandler().getNodesByNameFilter(
                    session, nodespec)

                if not nodes:
                    sys.stderr.write(
                        'No nodes matching nodespec [{0}]\n'.format(
                            args.nodespec))

                    sys.stderr.flush()

                    sys.exit(1)

            if args.software_profile:
                softwareprofile_names = args.software_profile.split(',')

                for softwareprofile_name in softwareprofile_names:
                    softwareprofile = SoftwareProfilesDbHandler().\
                        getSoftwareProfile(session, softwareprofile_name)

                    softwareprofiles.append(softwareprofile)

            if args.hardware_profile:
                hardwareprofile_names = args.hardware_profile.split(',')

                for hardwareprofile_name in hardwareprofile_names:
                    hardwareprofile = HardwareProfilesDbHandler().\
                        getHardwareProfile(session, hardwareprofile_name)

                    hardwareprofiles.append(hardwareprofile)

            # Create list of 'Tags' database objects
            tag_objs = self.get_tag_objects(session, args.tags)

            # Associate with nodes
            for node in nodes or []:
                for tag_obj in tag_objs:
                    if tag_obj in node.tags:
                        # Tag already exists
                        continue

                    node.tags.append(tag_obj)

                print(node.name, node.tags)

            # Associate with software profiles
            for softwareprofile in softwareprofiles:
                for tag_obj in tag_objs:
                    if tag_obj in softwareprofile.tags:
                        continue

                    softwareprofile.tags.append(tag_obj)

            # Associate with hardware profiles
            for hardwareprofile in hardwareprofiles:
                for tag_obj in tag_objs:
                    if tag_obj in hardwareprofile.tags:
                        continue

                    hardwareprofile.tags.append(tag_obj)

            session.commit()
        finally:
            DbManager().closeSession()

    def get_tag_objects(self, session, tags):
        """Given a list of (key, value) tuples, query database objects.

        Any tags that do not exist will be added to the session
        """

        tag_objs = []

        for key, value in tags:
            tag = TagsDbHandler().get_tag(session, key)
            if tag:
                tag_objs.append(tag)

                continue

            new_tag = Tags(key, value)
            tag_objs.append(new_tag)

            session.add(new_tag)

        return tag_objs

    def remove_tag(self, args):
        """Remove tags from specified resources"""

    def delete_tag(self, args):
        """Delete specific tags"""

        session = DbManager().openSession()

        for key in args.tags:
            tag_obj = session.query(Tags).filter(Tags.name == key).first()

            if tag_obj is None:
                sys.stderr.write('Tag [{0}] not found\n'.format(key))
                sys.stderr.flush()

                continue

            if not args.force and \
                    (tag_obj.nodes or
                     tag_obj.softwareprofiles or
                     tag_obj.hardwareprofiles):
                # Warn user if tag is associated with any resources

                print('Tag [{0}] is in use by the following resources:'.format(key))
                print()

                if tag_obj.nodes:
                    print('Nodes: ' + ' '.join([node.name for node in tag_obj.nodes]))

                if tag_obj.softwareprofiles:
                    print('Software profiles: ' + ' '.join([softwareprofile for softwareprofile in tag_obj.softwareprofiles]))

                if tag_obj.hardwareprofiles:
                    print('Hardware profiles: ' + ' '.join([hardwareprofile for hardwareprofile in tag_obj.hardwareprofiles]))

                print('Do you wish to delete this tag [N/y/a/?]? ')
                input = input('')

                if not input or input.lower().startswith('n'):
                    continue

                if input.lower().startswith('a'):
                    sys.stderr.write('Operation aborted by user.\n')
                    sys.stderr.flush()

                    break

                # TODO: display help on '?'

                print('Deleting tag [{0}]'.format(key))

            session.delete(tag_obj)

        session.commit()

    def list_tag(self, args):
        session = DbManager().openSession()

        try:
            tags = TagsDbHandler().get_tags(session)

            if not tags:
                sys.exit(0)

            for tag in tags:
                print('{0}: {1}'.format(tag.name, tag.value))

                if args.all_resources or args.nodes:
                    print('    ' + 'Node(s): ' + ' '.join([node.name for node in tag.nodes]))

                if args.all_resources or args.software_profiles:
                    print('    ' + 'Software profile(s): ' + ' '.join([softwareprofile.name for softwareprofile in tag.softwareprofiles]))
        finally:
            DbManager().closeSession()


def key_value_pair(arg):
    key, value = arg.split('=', 1)

    return key, value


if __name__ == '__main__':
    UctagCli().run()

