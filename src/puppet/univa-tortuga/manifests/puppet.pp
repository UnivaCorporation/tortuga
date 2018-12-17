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
  $pkgs = ['puppet-agent']

  ensure_packages($pkgs, {'ensure' => 'installed'})
}

class tortuga::puppet::config {
  require tortuga::puppet::package

  include tortuga::config

  $normalized_installer = downcase($tortuga::puppet::installer)

  augeas { 'configure_puppet_agent':
    context => '/files/etc/puppetlabs/puppet/puppet.conf',
    changes => [
      "set main/server ${normalized_installer}",
    ],
  }

  # configure puppet proxy settings

  if $tortuga::config::puppet_proxy_http_host {
    augeas { 'configure puppet proxy_http_host':
      context => '/files/etc/puppetlabs/puppet/puppet.conf',
      changes => [
        "set main/http_proxy_host ${tortuga::config::puppet_proxy_http_host}",
      ],
    }
  }

  if $tortuga::config::puppet_proxy_http_port {
    augeas { 'configure puppet proxy_http_port':
      context => '/files/etc/puppetlabs/puppet/puppet.conf',
      changes => [
        "set main/http_proxy_port ${tortuga::config::puppet_proxy_http_port}",
      ],
    }
  }

  if $tortuga::config::puppet_proxy_http_user {
    augeas { 'configure puppet proxy_http_user':
      context => '/files/etc/puppetlabs/puppet/puppet.conf',
      changes => [
        "set main/http_proxy_user ${tortuga::config::puppet_proxy_http_user}",
      ],
    }
  }

  if $tortuga::config::puppet_proxy_http_password {
    augeas { 'configure puppet proxy_http_password':
      context => '/files/etc/puppetlabs/puppet/puppet.conf',
      changes => [
        "set main/http_proxy_password ${tortuga::config::puppet_proxy_http_password}",
      ],
    }
  }

  augeas { 'disable deprecation warnings':
    context => '/files/etc/puppetlabs/puppet/puppet.conf',
    changes => 'set main/disable_warnings deprecations',
  }
}

class tortuga::puppet (
  String $installer = $::puppet_server,
) {
  contain tortuga::puppet::package
  contain tortuga::puppet::config
}
