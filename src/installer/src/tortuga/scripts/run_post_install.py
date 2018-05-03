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

import argparse
import sys
import os
import logging
from tortuga.kit.registry import get_kit_installer
from tortuga.kit.loader import load_kits


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def main():
    p = argparse.ArgumentParser()

    p.add_argument('-f', '--force', dest='force', action='store_true',
                   default=False)

    p.add_argument('name', help='Software profile name')
    p.add_argument('kit', help='Kit descriptor (NAME-VERSION-ITERATION)')
    p.add_argument('component', help='Component descriptor (NAME-VERSION)')

    args = p.parse_args()

    kitNameAndVersion, kitIteration = args.kit.rsplit('-', 1)
    kitName, kitVersion = kitNameAndVersion.split('-', 1)

    compName, _ = args.component.split('-', 2)

    flagFile = ('/opt/tortuga/var/run/actions/%s'
                '/component_%s_%s_post_install') % (
                    args.name, args.kit, args.component)

    if os.path.exists(flagFile):
        if not args.force:
            sys.stderr.write(
                'post-install component action for [%s] already run\n' % (
                    compName))

            sys.exit(1)

        # Remove the existing flag file, we're forcing a run
        os.unlink(flagFile)

    load_kits()
    kit_spec = (kitName, kitVersion, kitIteration)
    kit_installer = get_kit_installer(kit_spec)()
    c = kit_installer.get_component_installer(compName)
    c.run_action('post_install')

    logger.debug(
        'post_install component action run for [%s] from kit [%s]' % (
            args.component, args.kit))

    # Ensure destination directory exists
    if not os.path.exists(os.path.dirname(flagFile)):
        os.makedirs(os.path.dirname(flagFile))

    # touch flagFile
    open(flagFile, 'w').close()
