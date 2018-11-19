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

class tortuga::installer::sudo {
  require tortuga::installer::apache

  include tortuga::config

  ensure_packages(['sudo'], {'ensure' => 'installed'})

  $bin_dir = $tortuga::config::bin_dir
  $www_user = 'apache'

  file { '/etc/sudoers.d/tortuga':
    content => template('tortuga/tortuga-sudoers.erb'),
    mode    => '0440',
    require => Package['sudo'],
  }
}
