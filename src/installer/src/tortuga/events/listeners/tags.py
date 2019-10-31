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
from tortuga.web_service.database import dbm
from tortuga.events.listeners.base import BaseListener
from tortuga.events.types import BaseEvent, NodeTagsChanged
from tortuga.hardwareprofile.manager import HardwareProfileStoreManager
from tortuga.resourceAdapter.resourceAdapter import ResourceAdapter
from tortuga.resourceAdapter.resourceAdapterFactory import get_api
from tortuga.node.manager import NodeStoreManager


logger = logging.getLogger(__name__)


Session = sessionmaker(bind=dbm.engine)


class TagListener(BaseListener):
    name = 'push-tags-listener'
    event_types = [NodeTagsChanged]

    def run(self, event: BaseEvent):
        #
        # Make sure this is the right event type, and that it is relevant
        # for this resource adapter.
        #
        if not isinstance(event, NodeTagsChanged):
            return
        #
        # Do the actual tag update in the resource adapter
        #
        sess = Session()
        ra = self._get_resource_adapter(sess, event.node_id)
        ra.session = sess
        ra.push_tags(int(event.node_id))
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
