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

import datetime
from sqlalchemy.orm.session import Session

from tortuga.db.models.dataRequest import DataRequest
from tortuga.events.types import AddNodeRequestQueued
from tortuga.node.nodeManager import init_async_node_request
from tortuga.resourceAdapter.tasks import add_nodes


def enqueue_addnodes_request(session: Session, addNodesRequest: dict) -> str:
    """
    Enqueue add nodes request.

    request = {
        'addNodesRequest': { ... },
        'metadata': {
            'admin_id': ...
        }
    }
    """

    # determine id of user making request
    if 'metadata' in addNodesRequest and \
            'admin_id' in addNodesRequest['metadata']:
        admin_id = addNodesRequest['metadata']['admin_id']
    else:
        admin_id = None

    # persist request in database
    request = init_async_node_request(
        'ADD',
        addNodesRequest['addNodesRequest'],
        admin_id=admin_id
    )

    session.add(request)

    if 'data' in addNodesRequest['addNodesRequest']:
        data_request = _init_data_request(addNodesRequest['addNodesRequest']['data'], request.addHostSession)
        session.add(data_request)
    session.commit()

    #
    # Run async task
    #
    add_nodes.apply_async(
        args=(addNodesRequest,), task_id=request.addHostSession
    )

    #
    # Fire the add node request queued event
    #
    AddNodeRequestQueued.fire(request_id=request.id,
                              request=addNodesRequest['addNodesRequest'])

    return request.addHostSession

def _init_data_request(data, addHostSession):
    request = DataRequest()
    request.request = data
    request.timestamp = datetime.datetime.utcnow()
    request.addHostSession = addHostSession
    return request
