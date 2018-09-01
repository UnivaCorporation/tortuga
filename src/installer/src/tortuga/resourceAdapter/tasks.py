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
from tortuga.exceptions.nodeNotFound import NodeNotFound
from tortuga.exceptions.operationFailed import OperationFailed
from tortuga.tasks.celery import app


logger = logging.getLogger(__name__)


@app.task()
def add_nodes(session_id: str) -> None:
    try:
        with app.dbm.session() as session:
            process_addhost_request(session, session_id)
    except (OperationFailed, NodeNotFound) as exc:
        logger.error('Add nodes operation failed: {}'.format(exc))


@app.task()
def delete_nodes(transaction_id: str, nodespec: str, force: bool = False) -> None:
    try:
        with app.dbm.session() as session:
            process_delete_host_request(
                session, transaction_id, nodespec, force=force)
    except (OperationFailed, NodeNotFound) as exc:
        logger.error('Delete nodes operation failed: {}'.format(exc))
