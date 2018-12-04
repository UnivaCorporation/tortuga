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


class tortuga_kit_base::core (
  Variant[String, Undef] $proxy_uri = undef,
  Variant[String, Undef] $proxy_user = undef,
  Variant[String, Undef] $proxy_password = undef,
  Variant[String, Undef] $puppet_proxy_http_host = undef,
  Variant[Integer, Undef] $puppet_proxy_http_port = undef,
  Variant[String, Undef] $puppet_proxy_http_user = undef,
  Variant[String, Undef] $puppet_proxy_http_password = undef,
) {
  contain tortuga_kit_base::core::config
  contain tortuga_kit_base::core::actions
  contain tortuga_kit_base::core::done
}

class tortuga_kit_base::core::config {
  class { 'tortuga::config':
    proxy_uri                  => $tortuga_kit_base::core::proxy_uri,
    proxy_user                 => $tortuga_kit_base::core::proxy_user,
    proxy_password             => $tortuga_kit_base::core::proxy_password,
    puppet_proxy_http_host     => $tortuga_kit_base::core::puppet_proxy_http_host,
    puppet_proxy_http_port     => $tortuga_kit_base::core::puppet_proxy_http_port,
    puppet_proxy_http_user     => $tortuga_kit_base::core::puppet_proxy_http_user,
    puppet_proxy_http_password => $tortuga_kit_base::core::puppet_proxy_http_password,
  }
  contain tortuga::config

  class { 'tortuga::packages':
    require => Class['tortuga::config'],
  }

  contain tortuga::packages
}

class tortuga_kit_base::core::actions {
  # Incorporate classes defined in Hiera
  $classes = lookup('classes', {'merge' => 'unique', 'default_value' => []})
  if $classes {
    include($classes)
  }

  contain tortuga::compute
  contain tortuga_kit_base::core::cfmsecret
  contain tortuga_kit_base::core::ssh_server
  contain tortuga_kit_base::core::links
  contain tortuga_kit_base::common::nfs
  contain tortuga_kit_base::core::install
  contain tortuga_kit_base::core::certificate_authority
  contain tortuga::envscript

  contain tortuga_kit_base::core::post_install

  Class['tortuga_kit_base::core::install']
    -> Class['tortuga::envscript']
    -> Class['tortuga_kit_base::core::links']
}

class tortuga_kit_base::core::done {
  require tortuga_kit_base::core::actions

  tortuga_kit_base::installed { 'compute': }
}
