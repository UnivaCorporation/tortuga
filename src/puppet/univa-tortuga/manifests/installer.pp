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

class tortuga::installer (
  Variant[String, Undef] $puppet_server = undef,
  Variant[String, Undef] $database_engine = undef
) {
  if $puppet_server == undef {
    $puppet_server_arg = $::puppet_server
  } else {
    $puppet_server_arg = $puppet_server
  }

  if $database_engine == undef {
    $database_engine_arg = 'mysql'
  } else {
    $database_engine_arg = $database_engine
  }

  contain tortuga::installer::packages
  contain tortuga::installer::pre_conf
  contain tortuga::installer::puppetmaster
  contain tortuga::envscript
  contain tortuga::installer::redis
  contain tortuga::installer::apache
  contain tortuga::installer::cfm
  contain tortuga::installer::sudo
  contain tortuga::installer::basic

  class { 'tortuga::installer::database':
    database_engine => $database_engine_arg,
  }
  contain tortuga::installer::database

  class { 'tortuga::puppet':
    installer => $tortuga::config::installer_fqdn
  }

}
