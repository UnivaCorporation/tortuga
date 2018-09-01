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

from tortuga.events.types import AddNodeRequestQueued
from tortuga.resourceAdapter.tasks import add_nodes

from .addHostManager import _init_node_add_request


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

    #
    # Run async task
    #
    result = add_nodes.delay(addNodesRequest)

    # use Celery task id as 'addHostSession' and persist request in database
    request = _init_node_add_request(addNodesRequest, result.id)

    session.add(request)

    session.commit()

    #
    # Fire the add node request queued event
    #
    AddNodeRequestQueued.fire(request_id=request.id,
                              request=addNodesRequest['addNodesRequest'])

    return request.addHostSession
