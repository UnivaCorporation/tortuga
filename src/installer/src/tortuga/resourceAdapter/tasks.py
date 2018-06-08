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

from tortuga.tasks.celery import app
from tortuga.addhost.addHostRequest import process_addhost_request
from tortuga.addhost.deleteHostRequest import process_delete_host_request


@app.task()
def add_nodes(session_id):
    process_addhost_request(session_id)


@app.task()
def delete_nodes(transaction_id, nodespec):
    process_delete_host_request(transaction_id, nodespec)
