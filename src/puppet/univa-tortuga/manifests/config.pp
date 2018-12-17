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

class tortuga::config (
  Integer $int_web_port = $tortuga::params::int_web_port,
  String $instroot = $tortuga::params::instroot,
  String $installer_fqdn = $tortuga::params::installer_fqdn,
  Variant[String, Undef] $proxy_uri = undef,
  Variant[String, Undef] $proxy_user = undef,
  Variant[String, Undef] $proxy_password = undef,
  Variant[String, Undef] $puppet_proxy_http_host = undef,
  Variant[Integer, Undef] $puppet_proxy_http_port = undef,
  Variant[String, Undef] $puppet_proxy_http_user = undef,
  Variant[String, Undef] $puppet_proxy_http_password = undef,
) inherits tortuga::params {

  $config_dir = "${instroot}/config"
  $etc_dir = "${instroot}/etc"
  $bin_dir = "${instroot}/bin"

  $curl_base_cmd = 'curl --remote-name --fail'

  if $proxy_uri {
    if $proxy_user and $proxy_password {
      $curl_cmd = "${curl_base_cmd} --proxy-user ${proxy_user}:${proxy_password} --proxy ${proxy_uri}"
    } elsif $proxy_user {
      $curl_cmd = "${curl_base_cmd} --proxy-user ${proxy_user} --proxy ${proxy_uri}"
    } else {
      $curl_cmd = "${curl_base_cmd} --proxy ${proxy_uri}"
    }
  } else {
    $curl_cmd = $curl_base_cmd
  }
}
