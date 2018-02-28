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

#
# component_node_list()
#
# Description: Obtain hash of software profiles and their nodes by querying
#              Tortuga database directly (through the use of the helper
#              script get-component-node-list.sh)
#

require 'yaml'

module Puppet::Parser::Functions
  newfunction(:get_component_node_list, :type => :rvalue) do |args|
      cmd = "/opt/tortuga/etc/puppet/helpers/get-component-node-list.sh --kit-name #{args[0]} #{args[1]}"

      result = ''

      IO.popen(cmd, 'r') { |fp|
        result = YAML::load(fp)
      }

      return result
  end
end
