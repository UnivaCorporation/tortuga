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

NODE_STATE_CREATED = 'Created'
NODE_STATE_ALLOCATED = 'Allocated'
NODE_STATE_INSTALLED = 'Installed'
NODE_STATE_LAUNCHING = 'Launching'
NODE_STATE_PROVISIONED = 'Provisioned'
NODE_STATE_DELETED = 'Deleted'
NODE_STATE_UNRESPONSIVE = 'Unresponsive'
NODE_STATE_ERROR = 'Error'
NODE_STATE_EXPIRED = 'Expired'

# Iterable of all node states
ALLOWED_NODE_STATES = [
    NODE_STATE_CREATED,
    NODE_STATE_ALLOCATED,
    NODE_STATE_INSTALLED,
    NODE_STATE_LAUNCHING,
    NODE_STATE_PROVISIONED,
    NODE_STATE_DELETED,
    NODE_STATE_UNRESPONSIVE,
    NODE_STATE_ERROR,
    NODE_STATE_EXPIRED,
]
