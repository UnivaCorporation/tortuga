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

class tortuga::installer::mysqld::packages {
  $pkgs = [
    'rh-python36-python-PyMySQL'
  ]

  ensure_packages($pkgs, {'ensure' => 'installed'})
}

class tortuga::installer::mysqld::preinstall {
  require tortuga::installer::mysqld::packages

  ensure_resource('class', 'mysql::client', {})
  ensure_resource('class', 'mysql::server', {})
}

class tortuga::installer::mysqld::createdb {
  require tortuga::installer::mysqld::preinstall

  include tortuga::config

  $passwdfile = "${tortuga::config::instroot}/etc/db.passwd"

  mysql::db { $tortuga::config::database_name:
    user     => $tortuga::config::database_user,
    password => file($passwdfile),
    host     => 'localhost',
    grant    => ['all'],
  }
}

class tortuga::installer::mysqld {
  require tortuga::packages

  contain tortuga::installer::mysqld::packages
  contain tortuga::installer::mysqld::preinstall
  contain tortuga::installer::mysqld::createdb
}
