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

# Trigger Puppet agent on all managed nodes, or specific nodes for tags update
TAGS_CLUSTER_UPDATE=/etc/puppetlabs/code/environments/production/modules/tortuga_kit_uge/files/setup/tags-cluster-update.sh
SLURM_CLUSTER_UPDATE=/etc/puppetlabs/code/environments/production/modules/tortuga_kit_slurm/files/cluster-update.sh
if [ ! -z "$FACTER_node_tags_update" ]  || [ ! -z "$FACTER_softwareprofile_tags_update" ]; then
  if [ ! -f "$TAGS_CLUSTER_UPDATE" ]; then
    echo "Cannot find $TAGS_CLUSTER_UPDATE"
    exit 1
  fi
  set -x
  export FACTER_node_tags_update; export FACTER_softwareprofile_tags_update; $TAGS_CLUSTER_UPDATE
  exit $?
elif [ ! -z "$FACTER_slurm_cluster" ]; then
  if [ ! -f "$SLURM_CLUSTER_UPDATE" ]; then
    echo "Cannot find $SLURM_CLUSTER_UPDATE"
    exit 1
  fi
  export FACTER_slurm_cluster; $SLURM_CLUSTER_UPDATE
  exit $?
else
  echo "Normal cluster update puppet run"
  # Run Puppet on the installer first...
  /opt/puppetlabs/bin/puppet agent --onetime --no-daemonize
  exit $?
fi
