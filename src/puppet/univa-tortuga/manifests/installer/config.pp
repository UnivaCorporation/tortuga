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

class tortuga::installer::config {
  include tortuga::config

  exec { 'ssh_keys':
    command => "${tortuga::config::bin_dir}/create-ssh-keys",
    unless  => "${tortuga::config::bin_dir}/create-ssh-keys --stdout | diff -qU 4 /etc/puppet/modules/tortuga/manifests/compute/install_ssh_keys.pp - >/dev/null 2>&1",
  }
}
