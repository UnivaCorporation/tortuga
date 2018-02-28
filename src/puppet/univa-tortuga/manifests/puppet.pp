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

class tortuga::puppet::package {
  require tortuga::packages

  $pkgs = ['puppet-agent']

  ensure_packages($pkgs, {'ensure' => 'installed'})
}

class tortuga::puppet::config (
  $installer = $::puppet_server,
) {
  require tortuga::puppet::package

  $normalized_installer = downcase($installer)

  augeas { 'configure_puppet_agent':
    context => '/files/etc/puppetlabs/puppet/puppet.conf',
    changes => [
      "set main/server ${normalized_installer}",
      # 'set main/pluginsync true',
      # 'set agent/report true',
    ],
  }
}

class tortuga::puppet (
  $installer = $::puppet_server,
) {
  contain tortuga::puppet::package

  class { 'tortuga::puppet::config':
    installer => $installer,
  }
  contain tortuga::puppet::config
}
