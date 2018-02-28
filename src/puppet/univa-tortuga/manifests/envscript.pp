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

class tortuga::envscript {
  $instroot = $tortuga::config::instroot

  # Set up the 'environment' scripts with correct root dir
  file { "${tortuga::config::instroot}/etc/tortuga.sh":
    content => template('tortuga/tortuga.sh.erb'),
    mode    => '0644',
  }

  file { '/etc/profile.d/tortuga.sh':
    ensure  => link,
    target  => "${tortuga::config::instroot}/etc/tortuga.sh",
    require =>  File["${tortuga::config::instroot}/etc/tortuga.sh"],
  }


  file { "${tortuga::config::instroot}/etc/tortuga.csh":
    content => template('tortuga/tortuga.csh.erb'),
    mode    => '0644',
  }

  file { '/etc/profile.d/tortuga.csh':
    ensure  => link,
    target  => "${tortuga::config::instroot}/etc/tortuga.csh",
    require => File["${tortuga::config::instroot}/etc/tortuga.csh"],
  }
}
