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

import logging

from tortuga.addhost.addHostRequest import process_addhost_request
from tortuga.addhost.deleteHostRequest import process_delete_host_request
from tortuga.logging import RESOURCE_ADAPTER_NAMESPACE
from tortuga.tasks.celery import app


logger = logging.getLogger(RESOURCE_ADAPTER_NAMESPACE)


@app.task(bind=True)
def add_nodes(self, request: dict) -> None:
    with app.dbm.session() as session:
        # use Celery task id as 'addHostSession'
        process_addhost_request(session, request, self.request.id)


@app.task(bind=True)
def delete_nodes(self, nodespec: str, force: bool = False) -> None:
    with app.dbm.session() as session:
        # use Celery task id as 'addHostSession'
        process_delete_host_request(
            session, self.request.id, nodespec, force=force)
