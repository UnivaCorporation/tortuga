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

from sqlalchemy.orm.session import Session

from tortuga.db.nodeRequestsDbHandler import NodeRequestsDbHandler
from tortuga.events.types import AddNodeRequestComplete
from tortuga.exceptions.tortugaException import TortugaException

from .contextManager import AddHostSessionContextManager


logger = logging.getLogger('tortuga.addhost')


def process_addhost_request(session: Session, request: dict,
                            addHostSession: str):
    req = NodeRequestsDbHandler().get_by_addHostSession(
        session, addHostSession)

    if req is None:
        # session was deleted prior to being processed; nothing to do...
        return

    addHostRequest = request['addNodesRequest']

    #
    # Save this data so that we have it for firing the event below
    #
    evt_req_id = req.id
    evt_req_request = addHostRequest

    addHostRequest['addHostSession'] = addHostSession

    with AddHostSessionContextManager(req.addHostSession) as ahm:
        try:
            logger.debug(
                'Processing add host request [%s]', req.addHostSession)

            ahm.addHosts(session, addHostRequest)

            # Delete session log
            ahm.delete_session(req.addHostSession)

            # Completed node requests are deleted immediately
            session.delete(req)

            logger.debug(
                'Add host request [%s] processed successfully',
                req.addHostSession
            )
        except Exception as exc:  # noqa pylint: disable=broad-except
            if not isinstance(exc, TortugaException):
                logger.exception(
                    'Exception occurred during add host workflow')

            req.state = 'error'
            req.message = 'Exception: {}: {}'.format(
                exc.__class__.__name__, exc if exc.args else '<None>')
            req.last_update = datetime.datetime.utcnow()
        finally:
            session.commit()
            AddNodeRequestComplete.fire(request_id=evt_req_id,
                                        request=evt_req_request)
