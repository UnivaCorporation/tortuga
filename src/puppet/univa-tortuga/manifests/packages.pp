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

define add_package_source($baseurl, $cost=1000, $type='yum') {
  # Currently, we only support writing a YUM repository configuration.

  if $::osfamily == 'RedHat' {
    if $type == 'yum' {
      yumrepo { $name:
        baseurl  => $baseurl,
        descr    => "Repository for ${name}",
        enabled  => 1,
        gpgcheck => 0,
        cost     => $cost,
      }
    }
  }
}

class tortuga::packages {
  # This is necessary because this module is referenced as part of the
  # bootstrap before the ENC is available, so $::repos is undefined.

  if $::repos != undef {
    create_resources('add_package_source', $::repos)
  }
}
