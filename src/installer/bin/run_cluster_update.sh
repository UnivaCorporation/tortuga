#!/bin/sh

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


# Trigger Puppet agent on all managed nodes

# Run Puppet on the installer first...
/opt/puppetlabs/bin/puppet agent --onetime --no-daemonize

if [ ! -z "$FACTER_node_tags_update" ]; then
  echo "Node tags update: FACTER_node_tags_update=$FACTER_node_tags_update"
  export FACTER_node_tags_update; /opt/puppetlabs/bin/mco shell -A shell run "export FACTER_node_tags_update='$FACTER_node_tags_update'; /opt/puppetlabs/bin/puppet agent -t"
elif [ ! -z "$FACTER_softwareprofile_tags_update" ]; then
  echo "Software profile tags update: FACTER_softwareprofile_tags_update=$FACTER_softwareprofile_tags_update"
  export FACTER_softwareprofile_tags_update; /opt/puppetlabs/bin/mco shell -A shell run "export FACTER_softwareprofile_tags_update='$FACTER_softwareprofile_tags_update'; /opt/puppetlabs/bin/puppet agent -t"
else
  echo "Normal puppet run"
  /opt/puppetlabs/bin/mco puppet runonce
fi
