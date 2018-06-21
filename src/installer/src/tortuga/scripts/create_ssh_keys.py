#!/usr/bin/env python

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

import os
import subprocess
import sys

from tortuga.config.configManager import getfqdn


def readSshPublicKey(filename):
    with open(filename) as fp:
        buf = fp.read()

    arr = buf.rstrip().split(' ')

    name = '' if len(arr) == 2 else arr[2]

    return arr[0], arr[1], name


def main():
    if os.path.exists('/root/.ssh/id_rsa.pub'):
        # Attempt to use RSA key first
        sshKeyType, sshKey, sshKeyName = readSshPublicKey(
            '/root/.ssh/id_rsa.pub')
    elif os.path.exists('/root/.ssh/id_dsa.pub'):
        sshKeyType, sshKey, sshKeyName = readSshPublicKey(
            '/root/.ssh/id_dsa.pub')
    else:
        # Create a default SSH key
        hostName = getfqdn()

        cmd = 'ssh-keygen -t rsa -N "" -C "root@%s" -f /root/.ssh/id_rsa' % (
            hostName)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)

        _stdout, _stderr = p.communicate()

        retval = p.wait()
        if retval != 0:
            sys.stdout.write('Error: ssh-keygen debug output:\n%s\n' % (
                _stdout))
            sys.exit(1)

        sshKeyType, sshKey, sshKeyName = readSshPublicKey(
            '/root/.ssh/id_rsa.pub')

    if len(sys.argv) > 1 and sys.argv[1] == '--stdout':
        fp = sys.stdout
    else:
        fp = open('/etc/puppetlabs/code/environments/production/modules/tortuga/manifests/compute'
                  '/install_ssh_keys.pp', 'w')

    fp.write("""\
# DO NOT EDIT -- THIS FILE IS GENERATED DURING TORTUGA INSTALLATION

class tortuga::compute::install_ssh_keys {
""")

    if sshKeyType is not None:
        fp.write("""\
  ssh_authorized_key { '%s':
    ensure => present,
    key    => '%s',
    type   => '%s',
    user   => 'root'
  }
""" % (sshKeyName if sshKeyName else 'root', sshKey, sshKeyType))

    fp.write("}\n")

    fp.close()


if __name__ == '__main__':
    main()
