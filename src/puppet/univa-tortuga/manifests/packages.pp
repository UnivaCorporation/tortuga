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

class tortuga::packages (
  $repos = undef,
) {
  # This is necessary because this module is referenced as part of the
  # bootstrap before the ENC is available, so $::repos is undefined.
  if $repos == undef {
    $repos_arg = $::repos
  } else {
    $repos_arg = $repos
  }

  if $repos_arg != undef {
    $repos_arg.each |String $repo_name, Hash $repo_spec| {
      tortuga::add_package_source { $repo_name:
        baseurl => $repo_spec['baseurl'],
      }
    }
  }
}
