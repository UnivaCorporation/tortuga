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

define tortuga::pip_install {
  include tortuga::config

  # Use 'pip' in virtualenv (instead of system pip) to install packages

  if $tortuga::config::proxy_uri {
    $env = [
      "http_proxy=${tortuga::config::proxy_uri}"
    ]
  } else {
    $env = undef
  }

  exec { "pip_install_${name}":
    command => "${tortuga::config::instroot}/bin/pip install ${name}",
    unless  => "${tortuga::config::instroot}/bin/pip freeze | grep -qx \"^${name}==.*\"",
  }
}
