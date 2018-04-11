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

# pylint: disable=not-callable,no-member,multiple-statements

from tortuga.db.tortugaDbObjectHandler import TortugaDbObjectHandler
from tortuga.db.models.nodeRequest import NodeRequest


class NodeRequestsDbHandler(TortugaDbObjectHandler):
    """Accessor methods for NodeRequests table
    """

    def get_all(self, session): \
            # pylint: disable=no-self-use
        return session.query(NodeRequest).all()

    def get_by_id(self, session, node_request_id): \
            # pylint: disable=no-self-use
        return session.query(NodeRequest).get(node_request_id)

    def get_first_by_state(self, session, state): \
            # pylint: disable=no-self-use
        return session.query(NodeRequest).filter(
            NodeRequest.state == state).first()

    def get_by_addHostSession(self, session, addHostSession): \
            # pylint: disable=no-self-use
        return session.query(NodeRequest).filter(
            NodeRequest.addHostSession == addHostSession).first()
