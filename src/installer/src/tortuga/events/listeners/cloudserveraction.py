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

from .base import BaseListener
from ..types import CloudServerActionCreated

from tortuga.cloudserveraction.manager import CloudServerActionStoreManager
from tortuga.cloudserveraction.store import CloudServerActionStore
from tortuga.cloudserveraction.types import CloudServerAction
from tortuga.resourceAdapter.resourceAdapter import ResourceAdapter, \
    DEFAULT_CONFIGURATION_PROFILE_NAME
from tortuga.resourceAdapter.resourceAdapterFactory import get_api
from tortuga.types.application import Application


logger = logging.getLogger(__name__)


class CloudServerActionListener(BaseListener):
    event_types = [CloudServerActionCreated]

    def __init__(self, app: Application):
        super().__init__(app)
        self._store: CloudServerActionStore = \
            CloudServerActionStoreManager.get()

    def run(self, event: CloudServerActionCreated):
        csa: CloudServerAction = self._store.get(event.cloudserveraction_id)
        if csa is None:
            logger.warning(
                'Node action not found: {}'.format(
                    event.cloudserveraction_id))
            return

        try:
            self._run(csa)

        except Exception as ex:
            self._error(csa, ex)

    def _run(self, csa: CloudServerAction):
        csa.status = CloudServerAction.STATUS_PROCESSING
        self._store.save(csa)

        parts = csa.cloudserver_id.split(":")
        if len(parts) == 1:
            raise Exception("Node ID does not contain resource adapter")
        ra_name = parts.pop(0)

        ra = get_api(ra_name)
        logger.info('Found resource adapter: {}'.format(ra.__adaptername__))

        ccp_id = csa.cloudconnectorprofile_id
        if not ccp_id:
            ccp_id = DEFAULT_CONFIGURATION_PROFILE_NAME

        if csa.action == "shutdown":
            self._shutdown(ra, csa.cloudserver_id, ccp_id)

        elif csa.action == "reboot":
            self._shutdown(ra, csa.cloudserver_id, ccp_id)

        elif csa.action == "delete":
            self._delete(ra, csa.cloudserver_id, ccp_id)

        else:
            self._error(csa, Exception(
                'Action not supported: {}'.format(csa.action)))

    def _error(self, na: CloudServerAction, exception: Exception):
        na.status = CloudServerAction.STATUS_ERROR
        na.status_message = str(exception)
        self._store.save(na)
        raise exception

    def _shutdown(self, ra: ResourceAdapter, cs_id: str, ccp_id: str):
        pass

    def _reboot(self, ra: ResourceAdapter, cs_id: str, ccp_id: str):
        pass

    def _delete(self, ra: ResourceAdapter, cs_id: str, ccp_id: str):
        pass
