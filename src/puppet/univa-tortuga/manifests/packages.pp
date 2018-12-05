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

define tortuga::packages::add_package_source(
  String $baseurl,
  Integer $cost=1000,
  String $type='yum',
  Variant[String, Undef] $proxy = undef,
  Variant[String, Undef] $proxy_username = undef,
  Variant[String, Undef] $proxy_password = undef,
) {
  # Currently, we only support writing a YUM repository configuration.
  if $::facts['os']['family'] == 'RedHat' and $type == 'yum' {
    yumrepo { $name:
      baseurl        => $baseurl,
      descr          => "Repository for ${name}",
      enabled        => 1,
      gpgcheck       => 0,
      cost           => $cost,
      proxy          => $proxy,
      proxy_username => $proxy_username,
      proxy_password => $proxy_password,
    }
  }
}

class tortuga::packages (
  $repos = undef,
) {

  # This is necessary because this module is referenced as part of the
  # bootstrap before the ENC is available, so $::repos is undefined.

  if $repos != undef {
    create_resources('add_package_source', $repos)
    $repos.each |String $repo_name, Hash $repo_spec| {
      tortuga::packages::add_package_source { $repo_name:
        baseurl        => $repo_spec['baseurl'],
        proxy          => $tortuga::config::proxy_uri,
        proxy_username => $tortuga::config::proxy_user,
        proxy_password => $tortuga::config::proxy_password,
      }
    }
  }
}
