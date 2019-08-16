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

class tortuga::installer::apache::package {
  require tortuga::packages

  $pkgs = [
    'httpd',
    'mod_ssl',
  ]

  ensure_packages($pkgs, {'ensure' =>  'installed'})
}

class tortuga::installer::apache::config {
  require tortuga::installer::apache::package

  # Ensure SSLv3 is disabled by default (req'd for POODLE exploit)
  augeas { 'disable_ssl_v3':
    context => '/files/etc/httpd/conf.d/ssl.conf',
    changes => 'set VirtualHost/directive[.="SSLProtocol"]/arg[last()+1] -SSLv3',
    onlyif  => 'match VirtualHost/directive[.="SSLProtocol"][arg="-SSLv3"] size == 0',
  }

  augeas { 'stop_listening_80':
    context => '/files/etc/httpd/conf/httpd.conf',
    changes => 'rm directive[.="Listen"]'
  }
}

class tortuga::installer::apache::server {
  require tortuga::installer::apache::config

  service { 'httpd':
    ensure     => running,
    enable     => true,
    hasrestart => true,
    hasstatus  => true,
  }

}

class tortuga::installer::apache {
  contain tortuga::installer::apache::package
  contain tortuga::installer::apache::config
}
