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
import traceback
from typing import Optional

from sqlalchemy.orm import sessionmaker

from tortuga.cloudserveraction.manager import CloudServerActionStoreManager
from tortuga.cloudserveraction.store import CloudServerActionStore
from tortuga.cloudserveraction.types import CloudServerAction
from tortuga.resourceAdapter.resourceAdapter import ResourceAdapter, \
    DEFAULT_CONFIGURATION_PROFILE_NAME
from tortuga.resourceAdapter.resourceAdapterFactory import get_api
from tortuga.types.application import Application
from tortuga.web_service.database import dbm
from .base import BaseListener
from ..types import CloudServerActionCreated


logger = logging.getLogger(__name__)


class CloudServerActionListener(BaseListener):
    event_types = [CloudServerActionCreated]

    def __init__(self, app: Application):
        super().__init__(app)
        self._sess = sessionmaker(bind=dbm.engine)()
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
            msg = self._run(csa)

        except Exception as ex:
            csa.status = CloudServerAction.STATUS_ERROR
            csa.status_message = traceback.format_exc()
            self._store.save(csa)
            raise ex

        #
        # Assuming we get this far, then we assume the action successfully
        # ran, and we can mark the action as complete
        #
        csa.status = CloudServerAction.STATUS_COMPLETE
        if msg:
            csa.status_message = msg
        self._store.save(csa)

    def _run(self, csa: CloudServerAction) -> Optional[str]:
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
            msg = ("Cloud server ID does not contain resource adapter "
                   "prefix, skipping: {}".format(csa.cloudserver_id))
            logger.warning(msg)
            return msg
        ra_name = parts.pop(0)
        ra = get_api(ra_name)
        ra.session = self._sess
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

        #
        # Attempt a local delete, if possible
        #
        if csa.action == "delete":
            self._local_delete(ra_name, ccp_id, csa.cloudserver_id)

    def _local_delete(self, resource_adapter_name: str,
                      resource_adapter_profile: str, cloudserver_id: str):
        from tortuga.db.models.instanceMapping import InstanceMapping
        from tortuga.db.models.instanceMetadata import InstanceMetadata
        from tortuga.db.resourceAdapterConfigDbHandler import ResourceAdapterConfigDbHandler
        from tortuga.node.nodeApi import NodeApi

        node_api = NodeApi()

        #
        # Assume the node instance ID name is the last item in the
        # delimited cloud server ID
        #
        instance = cloudserver_id.split(":")[-1]

        #
        # Lookup the resource adapter configuration profile...
        #
        rac_api = ResourceAdapterConfigDbHandler()
        rac = rac_api.get(self._sess, resource_adapter_name,
                          resource_adapter_profile)

        #
        # Check the instance mapping to see if there is a matching
        # instance id...
        #
        im_list = self._sess.query(InstanceMapping).filter(
            InstanceMapping.instance == instance,
            InstanceMapping.resource_adapter_configuration_id == rac.id)
        #
        # Found something? Delete it and then return...
        #
        for im in im_list:
            node = im.node
            node_api.deleteNode(self._sess, node.name)

        #
        # Check the instance metadata so see if there is a
        # matching vm_name...
        #
        im_list = self._sess.query(InstanceMetadata).filter(
            InstanceMetadata.key == "vm_name",
            InstanceMetadata.value == instance
        )
        #
        # Found something? Delete it and then return...
        #
        for im in im_list:
            if im.instance.resource_adapter_configuration_id != rac.id:
                continue
            node = im.instance.node
            node_api.deleteNode(self._sess, node.name)
