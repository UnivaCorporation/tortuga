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
import json
import logging

from tortuga.db.dbManager import DbManager
from tortuga.db.nodeRequestsDbHandler import NodeRequestsDbHandler

from .contextManager import AddHostSessionContextManager

logger = logging.getLogger('tortuga.addhost')
logger.addHandler(logging.NullHandler())


def process_addhost_request(addHostSession):
    with DbManager().session() as session:
        req = NodeRequestsDbHandler().get_by_addHostSession(
            session, addHostSession)

        if req is None:
            # session was deleted prior to being processed; nothing to do...
            return

        addHostRequest = dict(list(json.loads(req.request).items()))

        addHostRequest['addHostSession'] = addHostSession

        with AddHostSessionContextManager(req.addHostSession) as ahm:
            try:
                logger.debug(
                    'process_addhost_request(): Processing add host'
                    ' request [%s]' % (req.addHostSession))

                ahm.addHosts(session, addHostRequest)

                # Delete session log
                ahm.delete_session(req.addHostSession)

                # Completed node requests are deleted immediately
                session.delete(req)

                logger.debug(
                    'Add host request [%s] processed successfully' % (
                        req.addHostSession))
            except Exception as exc:
                logger.exception(
                    'Fatal error occurred during add host workflow')

                req.state = 'error'
                req.message = str(exc)
                req.last_update = datetime.datetime.utcnow()
            finally:
                session.commit()
