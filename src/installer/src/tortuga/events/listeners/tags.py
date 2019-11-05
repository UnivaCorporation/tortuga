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

from sqlalchemy.orm import sessionmaker

from tortuga.db.resourceAdaptersDbHandler import ResourceAdaptersDbHandler
from tortuga.db.nodesDbHandler import NodesDbHandler
from tortuga.web_service.database import dbm
from tortuga.events.listeners.base import BaseListener
from tortuga.events.types.tag import BaseTagEvent
from tortuga.events.types import TagCreated, TagUpdated, TagDeleted
from tortuga.hardwareprofile.manager import HardwareProfileStoreManager
from tortuga.resourceAdapter.resourceAdapter import ResourceAdapter
from tortuga.resourceAdapter.resourceAdapterFactory import get_api
from tortuga.node.manager import NodeStoreManager
from tortuga.tags.types import Tag


logger = logging.getLogger(__name__)


Session = sessionmaker(bind=dbm.engine)


class TagChangeListener(BaseListener):
    name = 'push-tags-changes-to-resource-adapter'
    event_types = [TagCreated, TagUpdated, TagDeleted]

    def run(self, event: BaseTagEvent):
        #
        # Make sure this is the right event type, and that it is relevant
        # for this resource adapter.
        #
        if not isinstance(event, BaseTagEvent):
            return
        #
        # Parse the tag ID to get the metadata
        #
        object_type, object_id, tag_name = Tag.parse_id(event.tag_id)
        try:
            int(object_id)
        except ValueError:
            logger.error('Invalid object ID in tag ID: %s', event.tag_id)
        #
        # Currently only changes to node tags are supported
        #
        if object_type != 'node':
            return
        #
        # Managed tags need to have their prefix removed
        #
        if tag_name.startswith('managed:'):
            tag_name = tag_name.replace('managed:', '')
        #
        # Do the actual tag update in the resource adapter
        #
        sess = Session()
        ra = self._get_resource_adapter(sess, object_id)
        ra.session = sess
        node = NodesDbHandler().getNodeById(sess, int(object_id))
        if isinstance(event, TagDeleted):
            ra.unset_node_tag(node, tag_name)
        else:
            ra.set_node_tag(node, tag_name, event.value)
        sess.close()

    def _get_resource_adapter(self, sess: Session,
                              node_id: str) -> ResourceAdapter:
        node_store = NodeStoreManager.get()
        node = node_store.get(node_id)
        #
        # Lookup the hardware profile for the node
        #
        hwp_store = HardwareProfileStoreManager.get()
        hwp = hwp_store.get(node.hardwareprofile_id)
        #
        # Lookup the resource adapter for the hardware profile
        #
        ra_handler = ResourceAdaptersDbHandler()
        for db_ra in ra_handler.getResourceAdapterList(sess):
            if db_ra.id == int(hwp.resourceadapter_id):
                #
                # Get a instantiated ResourceAdapter instance
                #
                return get_api(db_ra.name)

        raise Exception('Resource adapter not found with ID: %s',
                        hwp.rsourceadapter_id)
