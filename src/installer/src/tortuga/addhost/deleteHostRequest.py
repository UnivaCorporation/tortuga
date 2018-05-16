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

# pylint: disable=no-member

import datetime
import logging
from tortuga.node.nodeApi import NodeApi
from tortuga.db.dbManager import DbManager
from tortuga.db.nodeRequestsDbHandler import NodeRequestsDbHandler
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.exceptions.nodeNotFound import NodeNotFound
from tortuga.addhost.addHostManager import AddHostManager


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

ahm = AddHostManager()


def process_delete_host_request(transaction_id, nodespec):
    session = DbManager().openSession()

    try:
        req = NodeRequestsDbHandler().get_by_addHostSession(
            session, transaction_id)
        if req is None:
            # Session was deleted prior to being process. Nothing to do...
            return

        ahm.update_session(transaction_id, running=True)

        logger.debug(
            'process_delete_host_request(): transaction_id=[{0}],'
            ' nodespec=[{1}]'.format(transaction_id, nodespec))

        try:
            NodeApi().deleteNode(nodespec)

            ahm.delete_session(transaction_id)

            session.delete(req)
        except NodeNotFound:
            ahm.delete_session(transaction_id)

            session.delete(req)
        except TortugaException as exc:
            logger.exception('Exception while deleting nodes')

            req.message = str(exc)

            req.state = 'error'

            req.last_update = datetime.datetime.utcnow()
        finally:
            ahm.update_session(transaction_id, running=False)
    finally:
        session.commit()

        DbManager().closeSession()
