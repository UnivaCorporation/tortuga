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

import threading
import uuid
from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.objects.tortugaObjectManager import TortugaObjectManager
from tortuga.objects.addHostStatus import AddHostStatus
from tortuga.db.nodeDbApi import NodeDbApi
from tortuga.exceptions.notFound import NotFound
from tortuga.resourceAdapter import resourceAdapterFactory
from tortuga.exceptions.resourceAdapterNotFound \
    import ResourceAdapterNotFound
from tortuga.db.softwareProfilesDbHandler \
    import SoftwareProfilesDbHandler
from tortuga.kit.actions import KitActionsManager
from tortuga.db.hardwareProfilesDbHandler \
    import HardwareProfilesDbHandler
from tortuga.wsapi.syncWsApi import SyncWsApi
from tortuga.db.tags import Tags
from tortuga.db.tagsDbHandler import TagsDbHandler
from tortuga.types import Singleton


class AddHostManager(TortugaObjectManager, Singleton):
    def __init__(self):
        super(AddHostManager, self).__init__()

        # Now do the class specific variable initialization
        self._addHostLock = threading.RLock()
        self._sessions = {}
        self._nodeDbApi = NodeDbApi()

    def addHosts(self, session, addHostRequest):
        """
        Raises:
            HardwareProfileNotFound
        """

        self.getLogger().debug('addHosts()')

        softwareProfilesDbHandler = SoftwareProfilesDbHandler()
        hardwareProfilesDbHandler = HardwareProfilesDbHandler()

        dbHardwareProfile = hardwareProfilesDbHandler.getHardwareProfile(
            session, addHostRequest['hardwareProfile'])

        if not dbHardwareProfile.resourceadapter:
            errmsg = ('Resource adapter not defined for hardware'
                      ' profile [%s]' % (dbHardwareProfile.name))

            self.getLogger().error(errmsg)

            raise ResourceAdapterNotFound(errmsg)

        softwareProfileName = addHostRequest['softwareProfile'] \
            if 'softwareProfile' in addHostRequest else None

        dbSoftwareProfile = softwareProfilesDbHandler.\
            getSoftwareProfile(session, softwareProfileName) \
            if softwareProfileName else None

        # Look up and/or create tags as necessary
        tags = get_tags(session, addHostRequest['tags']) \
            if 'tags' in addHostRequest else []

        ResourceAdapterClass = resourceAdapterFactory.getResourceAdapterClass(
            dbHardwareProfile.resourceadapter.name)

        resourceAdapter = ResourceAdapterClass(
            addHostSession=addHostRequest['addHostSession'])

        # Call the start() method of the resource adapter
        newNodes = resourceAdapter.start(
            addHostRequest, session, dbHardwareProfile,
            dbSoftwareProfile=dbSoftwareProfile)

        # Apply tags to new nodes
        for node in newNodes:
            node.tags = tags

        # Commit new node(s) to database
        session.commit()

        # Only perform post-add operations if we actually added a node
        if newNodes:
            if dbSoftwareProfile and not dbSoftwareProfile.isIdle:
                self.getLogger().info(
                    'Node(s) added to software profile [%s] and'
                    ' hardware profile [%s]' % (
                        dbSoftwareProfile.name
                        if dbSoftwareProfile else 'None',
                        dbHardwareProfile.name))

                newNodeNames = [tmpNode.name for tmpNode in newNodes]

                resourceAdapter.hookAction('add', newNodeNames)

                self.postAddHost(
                    dbHardwareProfile.name, softwareProfileName,
                    addHostRequest['addHostSession'])

                resourceAdapter.hookAction('start', newNodeNames)

        self.getLogger().debug('Add host workflow complete')

    def postAddHost(self, hardwareProfileName, softwareProfileName,
                    addHostSession):
        """Perform post add host operations"""

        self.getLogger().debug(
            'postAddHost(): hardwareProfileName=[%s]'
            ' softwareProfileName=[%s] addHostSession=[%s]' % (
                hardwareProfileName, softwareProfileName, addHostSession))

        mgr = KitActionsManager()

        mgr.post_add_host(
            hardwareProfileName, softwareProfileName, addHostSession)

        # Always go over the web service for this call.
        SyncWsApi().scheduleClusterUpdate(updateReason='Node(s) added')

    def updateStatus(self, addHostSession, msg):
        self._addHostLock.acquire()

        try:
            if addHostSession not in self._sessions:
                self.getLogger().warn(
                    'updateStatus(): unknown session ID [%s]' % (
                        addHostSession))

                return

            addHostStatus = self._sessions[addHostSession]['status']

            addHostStatus.getMessageList().append(msg)
        finally:
            self._addHostLock.release()

    def getStatus(self, session: str, startMessage: int,
                  getNodes: bool) -> AddHostStatus:
        """
        Raises:
            NotFound
        """
        with self._addHostLock:
            nodeList = self._nodeDbApi.getNodesByAddHostSession(session) \
                if getNodes else TortugaObjectList()

            # Lock and copy for data consistency
            if session not in self._sessions:
                raise NotFound('Invalid add host session ID [%s]' % (session))

            sessionDict = self._sessions.get(session)

            statusCopy = AddHostStatus()

            # Copy simple data
            for key in sessionDict['status'].getKeys():
                statusCopy.set(key, sessionDict['status'].get(key))

            # Get slice of status messages
            messages = sessionDict['status'].getMessageList()[startMessage:]

            statusCopy.setMessageList(messages)

            if nodeList:
                statusCopy.getNodeList().extend(nodeList)

            return statusCopy

    def createNewSession(self) -> str:
        self.getLogger().debug('createNewSession()')

        with self._addHostLock:
            # Create new add nodes session
            session_id = str(uuid.uuid4())

            self._sessions[session_id] = {
                'status': AddHostStatus(),
            }

            return session_id

    def delete_session(self, session_id):
        """TODO: currently a no-op"""

    def delete_sessions(self, session_ids):
        """Bulk session deletion

        Currently only called when deleting nodes
        """

        self.getLogger().debug('delete_sessions()')

        with self._addHostLock:
            for session_id in session_ids:
                if session_id in self._sessions:
                    self.getLogger().debug(
                        'Deleting session [{0}]'.format(session_id))

                    del self._sessions[session_id]

    def update_session(self, session_id, running=None):
        self.getLogger().debug(
            'Updating add host session [%s] (status: running=%s)' % (
                session_id, str(running)))

        with self._addHostLock:
            self._sessions[session_id]['status'].setIsRunning(running)


def get_tags(session, tagdict):
    tags = []

    for key, value in list(tagdict.items()):
        tag = TagsDbHandler().get_tag(session, key, value=value)
        if not tag:
            tag = Tags(key, value)

        tags.append(tag)

    return tags
