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

class tortuga_kit_base::installer::post_install {
  require tortuga::installer

  tortuga::run_post_install { 'installer_post_install':
    kitdescr  => $tortuga_kit_base::config::kitdescr,
    compdescr => $tortuga_kit_base::installer::compdescr,
  }
}

class tortuga_kit_base::installer (
  $database_engine = 'sqlite',
  $proxy_hash = {},
) {
  include tortuga::config
  include tortuga_kit_base::config

  $compdescr = "installer-${tortuga_kit_base::config::major_version}"

  # Incorporate classes defined in Hiera
  $classes = lookup('classes', {'merge' => 'unique', 'default_value' => []})
  if $classes {
    include($classes)
  }

  contain tortuga_kit_base::installer::actions
  contain tortuga_kit_base::installer::done
}

class tortuga_kit_base::installer::actions {

  contain tortuga::packages

  class { 'tortuga::installer':
    database_engine => $tortuga_kit_base::installer::database_engine,
  }
  contain tortuga::installer

  contain tortuga_kit_base::provisioning::packages
  contain tortuga_kit_base::installer::post_install
  contain tortuga_kit_base::installer::ntpd

  class { 'tortuga_kit_base::installer::apache':
    proxy_hash => $tortuga_kit_base::installer::proxy_hash,
  }
  contain tortuga_kit_base::installer::apache

  contain tortuga_kit_base::installer::celery
  contain tortuga_kit_base::installer::webservice
  contain tortuga_kit_base::installer::ssh
}

class tortuga_kit_base::installer::done {
  require tortuga_kit_base::installer::actions

  tortuga_kit_base::installed { 'installer': }
}
