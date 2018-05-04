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

"""
Update Tortuga Hiera configuration
"""

import os.path
import sys
import shutil
import yaml


def main():
    if len(sys.argv) != 2:
        print('usage: %s <hostname>' % (os.path.basename(sys.argv[0])))
        sys.exit(1)

    fn = ('/etc/puppetlabs/code/environments/production/data'
          '/tortuga-common.yaml')

    with open(fn) as fp:
        d = yaml.load(fp)

    d['puppet_server'] = sys.argv[1]

    with open(fn + '.new', 'w') as fpOut:
        fpOut.write(yaml.dump(d, explicit_start=True,
                              default_flow_style=False))

    shutil.move(fn + '.new', fn)
