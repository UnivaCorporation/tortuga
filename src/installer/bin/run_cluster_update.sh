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

# select only associated qmaster nodes
function node_mco_param() {
  local node=$1
  local mco_param=
  for cl in $(uge-cluster list 2> /dev/null); do
    for execd_sp in $(uge-cluster show $cl --list-execd-swprofiles 2> /dev/null); do
      execd_nodes=$(get-software-profile-nodes --software-profile $execd_sp)
      if [[ "$execd_nodes" = *"$node"* ]]; then
        for qmaster_sp in $(uge-cluster show $cl --list-qmaster-swprofiles 2> /dev/null); do
          for qmaster_node in $(get-software-profile-nodes --software-profile $qmaster_sp); do
            mco_param="$mco_param -I ${qmaster_node%%.*}"
          done
        done
        br=1
        break
      fi
    done
    if [ ! -z "$br" ]; then
      break
    fi
  done
  if [ -z "$br" ]; then
    echo "-I ${node%%.*}"
  else
    echo $mco_param
  fi
}

function swp_mco_param() {
  local swp=$1
  local mco_param=
  for cl in $(uge-cluster list 2> /dev/null); do
    execd_swps=$(uge-cluster show $cl --list-execd-swprofiles 2> /dev/null)
    if [[ "$execd_swps" = *"$swp"* ]]; then
      for qmaster_swp in $(uge-cluster show $cl --list-qmaster-swprofiles 2> /dev/null); do
        for qmaster_node in $(get-node-status -l --software-profile $qmaster_swp --installed); do
          mco_param="$mco_param -I ${qmaster_node%%.*}"
        done
      done
    fi
  done
  if [ -z "$mco_param" ]; then
    for node in $(get-software-profile-nodes --software-profile $swp); do
      mco_param="$mco_param -I $node"
    done
  fi
  echo $mco_param
}

if [ ! -z "$FACTER_node_tags_update" ]; then
  echo "Node tags update: FACTER_node_tags_update=$FACTER_node_tags_update"
  node=$(echo "$FACTER_node_tags_update" | python -c 'import sys, json; print(json.load(sys.stdin)["name"])')
  if [ $? -ne 0 ] || [ -z "$node" ]; then
    echo "Cannot get node from tags update"
    exit 1
  fi

  mco_param="$(node_mco_param $node)"
  echo "$mco_param"

  export FACTER_node_tags_update; /opt/puppetlabs/bin/mco shell $mco_param run "export FACTER_node_tags_update='$FACTER_node_tags_update'; /opt/puppetlabs/bin/puppet agent -t"
elif [ ! -z "$FACTER_softwareprofile_tags_update" ]; then
  echo "Software profile tags update: FACTER_softwareprofile_tags_update=$FACTER_softwareprofile_tags_update"
  swp=$(echo "$FACTER_softwareprofile_tags_update" | python -c 'import sys, json; print(json.load(sys.stdin)["name"])')
  if [ $? -ne 0 ] || [ -z "$swp" ]; then
    echo "Cannot get software profile from tags update"
    exit 1
  fi
  mco_param="$(swp_mco_param $swp)"
  echo "$mco_param"
  if [ -z "$mco_param" ]; then
    echo "Didn't find any appropriate mco identity for software profile $swp"
    exit 1
  fi
  export FACTER_softwareprofile_tags_update; /opt/puppetlabs/bin/mco shell $mco_param run "export FACTER_softwareprofile_tags_update='$FACTER_softwareprofile_tags_update'; /opt/puppetlabs/bin/puppet agent -t"
else
  echo "Normal puppet run"
  # Run Puppet on the installer first...
  /opt/puppetlabs/bin/puppet agent --onetime --no-daemonize
  /opt/puppetlabs/bin/mco puppet runonce
fi
