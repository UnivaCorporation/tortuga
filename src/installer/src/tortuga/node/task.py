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

from sqlalchemy.orm.session import Session
from tortuga.events.types import DeleteNodeRequestQueued
from tortuga.node import state
from tortuga.node.nodeManager import NodeManager, init_async_node_request
from tortuga.resourceAdapter.tasks import delete_nodes


def enqueue_delete_hosts_request(session: Session, nodespec: str, force: bool):
    # use Celery task id as 'addHostSession' and persist request in database
    request = init_async_node_request('DELETE', nodespec)

    session.add(request)

    session.commit()

    #
    # Run async task
    #
    delete_nodes.delay(nodespec, force=force)

    delete_nodes.apply_async(
        args=(nodespec,), kwargs=dict(force=force),
        task_id=request.addHostSession,
    )

    #
    # Fire the delete node request queued event
    #
    evt_request = {
        'name': nodespec,
        'force': force,
    }
    DeleteNodeRequestQueued.fire(request_id=request.id, request=evt_request)

    return request.addHostSession
