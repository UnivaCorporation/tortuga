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

# pylint: disable=no-member,maybe-no-member

import logging
import threading
import uuid
from typing import Iterable, List, Optional

from sqlalchemy.orm.session import Session

from tortuga.db.hardwareProfilesDbHandler import HardwareProfilesDbHandler
from tortuga.db.models.nodeTag import NodeTag
from tortuga.db.nodeDbApi import NodeDbApi
from tortuga.db.softwareProfilesDbHandler import SoftwareProfilesDbHandler
from tortuga.db.tagsDbApiMixin import TagsDbApiMixin
from tortuga.exceptions.notFound import NotFound
from tortuga.exceptions.nodeNotFound import NodeNotFound
from tortuga.exceptions.resourceAdapterNotFound import ResourceAdapterNotFound
from tortuga.kit.actions import KitActionsManager
from tortuga.logging import ADD_HOST_NAMESPACE
from tortuga.objects.addHostStatus import AddHostStatus
from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.objects.tortugaObjectManager import TortugaObjectManager
from tortuga.objectstore.manager import ObjectStoreManager
from tortuga.resourceAdapter import resourceAdapterFactory
from tortuga.wsapi.syncWsApi import SyncWsApi


class AddHostManager(TagsDbApiMixin, TortugaObjectManager):
    tag_model = NodeTag

    def __init__(self):
        super(AddHostManager, self).__init__()

        # Now do the class specific variable initialization
        self._addHostLock = threading.RLock()
        self._logger = logging.getLogger(ADD_HOST_NAMESPACE)
        self._nodeDbApi = NodeDbApi()
        self._sessions = ObjectStoreManager.get(namespace='add-host-manager')

    def addHosts(self, session: Session, addHostRequest: dict) -> None:
        """
        Raises:
            HardwareProfileNotFound
            ResourceAdapterNotFound
        """

        self._logger.debug('addHosts()')

        #
        # Check if a node with the same name already exists. If it does,
        # then we should not go any further, as you cannot re-register
        # a node. Instead, throw an exception so that callers can deal with
        # the problem in an appropriate fashion.
        #
        node_details = addHostRequest.get('nodeDetails', [])
        for node_detail in node_details:
            node_name = node_detail.get('name', '').strip()
            if node_name:
                try:
                    self._nodeDbApi.getNode(session, node_name)
                    raise Exception("Node already exists: {}".format(node_name))
                except NodeNotFound:
                    pass

        dbHardwareProfile = \
            HardwareProfilesDbHandler().getHardwareProfile(
                session, addHostRequest['hardwareProfile'])

        if not dbHardwareProfile.resourceadapter:
            errmsg = ('Resource adapter not defined for hardware'
                      ' profile [%s]' % (dbHardwareProfile.name))

            self._logger.error(errmsg)

            raise ResourceAdapterNotFound(errmsg)

        softwareProfileName = addHostRequest['softwareProfile'] \
            if 'softwareProfile' in addHostRequest else None

        dbSoftwareProfile = \
            SoftwareProfilesDbHandler().getSoftwareProfile(
                session, softwareProfileName) \
            if softwareProfileName else None

        ResourceAdapterClass = \
            resourceAdapterFactory.get_resourceadapter_class(
                dbHardwareProfile.resourceadapter.name)

        resourceAdapter = ResourceAdapterClass(
            addHostSession=addHostRequest['addHostSession'])

        resourceAdapter.session = session

        # Call the start() method of the resource adapter
        newNodes = resourceAdapter.start(
            addHostRequest, session, dbHardwareProfile,
            dbSoftwareProfile=dbSoftwareProfile)

        session.add_all(newNodes)
        session.flush()

        if 'tags' in addHostRequest and addHostRequest['tags']:
            for node in newNodes:
                self._set_tags(node, addHostRequest['tags'], merge=True)

        # Commit new node(s) to database
        session.commit()

        # Only perform post-add operations if we actually added a node
        if newNodes:
            self._logger.info(
                'Node(s) added to software profile [%s] and'
                ' hardware profile [%s]',
                dbSoftwareProfile.name if dbSoftwareProfile else 'None',
                dbHardwareProfile.name,
            )

            newNodeNames = [tmpNode.name for tmpNode in newNodes]

            resourceAdapter.hookAction('add', newNodeNames)

            self.postAddHost(
                session, dbHardwareProfile.name, softwareProfileName,
                addHostRequest['addHostSession'])

            resourceAdapter.hookAction('start', newNodeNames)

        self._logger.debug('Add host workflow complete')

    def postAddHost(self, session: Session, hardwareProfileName: str,
                    softwareProfileName: Optional[str],
                    addHostSession: str) -> None:
        """
        Perform post add host operations
        """

        self._logger.debug(
            'postAddHost(): hardwareProfileName=[%s]'
            ' softwareProfileName=[%s] addHostSession=[%s]' % (
                hardwareProfileName, softwareProfileName, addHostSession))

        # this query is redundant; in the calling method, we already have
        # a list of Node (db) objects
        from tortuga.node.nodeApi import NodeApi
        nodes = NodeApi().getNodesByAddHostSession(session, addHostSession)

        mgr = KitActionsManager()
        mgr.session = session

        mgr.post_add_host(
            hardwareProfileName,
            softwareProfileName,
            nodes
        )

        # Always go over the web service for this call.
        SyncWsApi().scheduleClusterUpdate(updateReason='Node(s) added')

    def updateStatus(self, addHostSession: str, msg: str) -> None:
        self._addHostLock.acquire()

        try:
            if not self._sessions.exists(addHostSession):
                self._logger.warning(
                    'updateStatus(): unknown session ID [%s]' % (
                        addHostSession))

                return

            addHostStatus = AddHostStatus.getFromDict(
                self._sessions.get(addHostSession)['status'])

            addHostStatus.getMessageList().append(msg)
        finally:
            self._addHostLock.release()

    def getStatus(self, db_session: Session, session: str,
                  startMessage: int, getNodes: bool) -> AddHostStatus:
        """
        Raises:
            NotFound
        """
        with self._addHostLock:
            nodeList = self._nodeDbApi.getNodesByAddHostSession(
                db_session, session) if getNodes else TortugaObjectList()

            # Lock and copy for data consistency
            if not self._sessions.exists(session):
                raise NotFound('Invalid add host session ID [%s]' % (session))

            session = self._sessions.get(session)

            status_copy = AddHostStatus()

            # Copy simple data
            status = AddHostStatus.getFromDict(session['status'])
            for key in status.getKeys():
                status_copy.set(key, status.get(key))

            # Get slice of status messages
            messages = status.getMessageList()[startMessage:]

            status_copy.setMessageList(messages)

            if nodeList:
                status_copy.getNodeList().extend(nodeList)

            return status_copy

    def createNewSession(self) -> str:
        self._logger.debug('createNewSession()')

        with self._addHostLock:
            # Create new add nodes session
            session_id = str(uuid.uuid4())

            self._sessions.set(
                session_id,
                {'status': AddHostStatus().getCleanDict()}
            )

            return session_id

    def delete_session(self, session_id: str) -> None:
        """TODO: currently a no-op"""

    def delete_sessions(self, session_ids: Iterable[str]) -> None:
        """Bulk session deletion

        Currently only called when deleting nodes
        """

        if not session_ids:
            self._logger.debug(
                'delete_sessions() called with empty session_ids list'
            )

            return

        self._logger.debug(
            'delete_sessions(): session_ids=[%s]', ' '.join(session_ids))

        with self._addHostLock:
            for session_id in session_ids:
                if not self._sessions.exists(session_id):
                    continue

                self._logger.debug('Deleting addhost session [%s]', session_id)

                self._sessions.delete(session_id)

    def update_session(
            self, session_id: str, running: Optional[bool] = None):
        self._logger.debug(
            'Updating add host session [%s] (status: running=%s)' % (
                session_id, str(running)))

        with self._addHostLock:
            session = self._sessions.get(session_id)
            status = AddHostStatus.getFromDict(session['status'])
            session['status'] = status.getCleanDict()
            self._sessions.set(session_id, session)
