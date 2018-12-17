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

define tortuga::add_package_source(
  String $baseurl,
  Integer $cost=1000,
  String $type='yum',
) {
  # Currently, we only support writing a YUM repository configuration.
  if $::facts['os']['family'] == 'RedHat' and $type == 'yum' {
    yumrepo { $name:
      baseurl        => $baseurl,
      descr          => "Repository for ${name}",
      enabled        => 1,
      gpgcheck       => 0,
      cost           => $cost,
      proxy          => $tortuga::config::proxy_uri,
      proxy_username => $tortuga::config::proxy_user,
      proxy_password => $tortuga::config::proxy_password,
    }
  }
}