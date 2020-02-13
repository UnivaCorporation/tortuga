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
        #
        # Lookup the action referenced in the event
        #
        csa: CloudServerAction = self._store.get(event.cloudserveraction_id)
        if csa is None:
            logger.warning(
                'Node action not found: {}'.format(
                    event.cloudserveraction_id))
            return

        #
        # Wrap everything so we can capture any exceptions and log them to
        # the action
        #
        try:
            self._run(csa)

        except Exception as ex:
            self._error(csa, ex)

        #
        # Assuming we get this far, then we assume the action successfully
        # ran, and we can mark the action as complete
        #
        csa.status = CloudServerAction.STATUS_COMPLETE
        self._store.save(csa)

    def _run(self, csa: CloudServerAction):
        #
        # Mark the action as "running"
        #
        csa.status = CloudServerAction.STATUS_PROCESSING
        self._store.save(csa)

        #
        # Get the resource adapter
        #
        parts = csa.cloudserver_id.split(":")
        if len(parts) == 1:
            raise Exception("Node ID does not contain resource adapter")
        ra_name = parts.pop(0)
        ra = get_api(ra_name)
        logger.info('Found resource adapter: {}'.format(ra.__adaptername__))

        #
        # Get the cloud connector profile ID
        #
        ccp_id = csa.cloudconnectorprofile_id
        if not ccp_id:
            ccp_id = DEFAULT_CONFIGURATION_PROFILE_NAME

        #
        # Get the action method from the resource adapter instance. Supported
        # actions are any methods on the ResourceAdapter instance that have
        # the method name cloudserveraction_<action-name>
        #
        action_name = "cloudserveraction_{}".format(csa.action)
        action = getattr(ra, action_name)
        if not action:
            raise Exception('Action not supported: {}'.format(csa.action))

        #
        # Get any additional action parameters
        #
        if csa.action_params:
            if not isinstance(csa.action_params, dict):
                raise Exception(
                    "Invalid action_params: {}".format(csa.action_params))
            params = csa.action_params
        else:
            params = {}

        #
        # Run the action!
        #
        action(ccp_id, csa.cloudserver_id, **params)

    def _error(self, na: CloudServerAction, exception: Exception):
        na.status = CloudServerAction.STATUS_ERROR
        na.status_message = str(exception)
        self._store.save(na)
        raise exception
