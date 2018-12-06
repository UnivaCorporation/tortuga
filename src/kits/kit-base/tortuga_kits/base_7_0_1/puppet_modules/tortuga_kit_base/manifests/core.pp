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


class tortuga_kit_base::core {
  # Incorporate classes defined in Hiera
  $classes = lookup('classes', {'merge' => 'unique', 'default_value' => []})
  if $classes {
    include($classes)
  }

  contain tortuga_kit_base::core::packages
  contain tortuga_kit_base::core::worker
  contain tortuga_kit_base::core::installed
}

class tortuga_kit_base::core::packages {
  contain tortuga::packages
}

class tortuga_kit_base::core::worker {
  require tortuga_kit_base::core::packages

  contain tortuga::compute
  contain tortuga_kit_base::core::cfmsecret
  contain tortuga_kit_base::core::ntpd
  contain tortuga_kit_base::core::ssh_server
  contain tortuga_kit_base::core::links
  contain tortuga_kit_base::common::nfs
  contain tortuga_kit_base::core::install
  contain tortuga::envscript

  contain tortuga_kit_base::core::post_install

  Class['tortuga_kit_base::core::install']
    -> Class['tortuga::envscript']
    -> Class['tortuga_kit_base::core::links']
}

class tortuga_kit_base::core::installed {
  require tortuga_kit_base::core::worker

  tortuga_kit_base::installed { 'compute': }
}
