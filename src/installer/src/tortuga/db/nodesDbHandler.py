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

# pylint: disable=not-callable,no-member,multiple-statements,no-self-use
from typing import Dict, List, Optional, Union

from sqlalchemy import and_, func, or_
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session

from tortuga.config.configManager import getfqdn
from tortuga.db.softwareProfilesDbHandler import SoftwareProfilesDbHandler
from tortuga.db.tortugaDbObjectHandler import TortugaDbObjectHandler
from tortuga.exceptions.nodeNotFound import NodeNotFound
from .models.nic import Nic
from .models.node import Node
from .models.softwareProfile import SoftwareProfile

Tags = Dict[str, Optional[str]]


class NodesDbHandler(TortugaDbObjectHandler):
    """
    This class handles nodes table.
    """

    def __init__(self):
        super().__init__()

        self._softwareProfilesDbHandler = SoftwareProfilesDbHandler()

    def getNode(self, session: Session, name: str) -> Node:
        """
        Return node.

        Raises:
            NodeNotFound
        """

        try:
            if '.' in name:
                # Attempt exact match on fully-qualfied name
                return session.query(Node).filter(
                    func.lower(Node.name) == name.lower()).one()

            # 'name' is short host name; attempt to match on either short
            # host name or any host starting with same host name
            return session.query(Node).filter(
                or_(func.lower(Node.name) == name.lower(),
                    func.lower(Node.name).like(name.lower() + '.%'))).one()
        except NoResultFound:
            raise NodeNotFound("Node [%s] not found" % (name))

    def get_installer_node(self, session: Session) -> Node:
        """
        Return installer node derived from searching for all software
        profiles with type 'installer'.

        Raises:
            NodeNotFound
        """

        installer_swprofiles = \
            SoftwareProfilesDbHandler().getSoftwareProfileList(
                session,
                profile_type='installer'
            )

        if not installer_swprofiles:
            raise NodeNotFound(
                'No installer software profiles found'
            )

        installer_nodes = installer_swprofiles[0].nodes
        if not installer_nodes:
            raise NodeNotFound(
                'No installer node found in software profile {}'.format(
                    installer_swprofiles[0].name
                )
            )

        return installer_nodes[0]

    def getNodesByTags(self, session: Session,
                       tags: Optional[Tags] = None):
        """
        Gets nodes by tag(s). Tags is a dictionary of key/value pairs to
        match against.

        :param session: a SQLAlchemy database session
        :param tags:    a dictionary of key/value tag pairs

        :return: a list of nodes

        """
        searchspec = []

        # iterate over list of tag tuples making SQLAlchemy search
        # specification
        if tags:
            for name, value in tags.items():
                if value:
                    #
                    # Match both name and value
                    #
                    searchspec.append(and_(
                        Node.tags.any(name=name),
                        Node.tags.any(value=value)
                    ))
                else:
                    #
                    # Match name only
                    #
                    searchspec.append(Node.tags.any(name=name))

        return session.query(Node).filter(or_(*searchspec)).all()

    def getNodesByAddHostSession(self, session: Session, ahSession: str) \
            -> List[Node]:
        """
        Get nodes by add host session
        Returns a list of nodes
        """

        self._logger.debug(
            'getNodesByAddHostSession(): ahSession [%s]' % (ahSession))

        return session.query(Node).filter(
            Node.addHostSession == ahSession).order_by(Node.name).all()

    def getNodesByNameFilter(
            self,
            session: Session,
            filter_spec: Union[str, list],
            include_installer: Optional[bool] = True) -> List[Node]:
        """
        Filter follows SQL "LIKE" semantics (ie. "something%")

        Exclude installer node from node list by setting
        'include_installer' to False.

        Returns a list of Node
        """

        filter_spec_list = [filter_spec] \
            if not isinstance(filter_spec, list) else filter_spec

        node_filter = []

        for filter_spec_item in filter_spec_list:
            if '.' not in filter_spec_item:
                # Match exactly (ie. "hostname-01")
                node_filter.append(Node.name.like(filter_spec_item))

                # Match host name only (ie. "hostname-01.%")
                node_filter.append(Node.name.like(filter_spec_item + '.%'))

                continue

            # Match fully-qualified node names exactly
            # (ie. "hostname-01.domain")
            node_filter.append(Node.name.like(filter_spec_item))

        if not include_installer:
            installer_fqdn = getfqdn()

            return session.query(Node).filter(
                and_(
                    Node.name != installer_fqdn,
                    or_(*node_filter)
                )
            ).all()

        return session.query(Node).filter(or_(*node_filter)).all()

    def getNodeById(self, session: Session, _id: int) -> Node:
        """
        Return node.

        Raises:
            NodeNotFound
        """

        self._logger.debug('Retrieving node by ID [%s]' % (_id))

        dbNode = session.query(Node).get(_id)

        if not dbNode:
            raise NodeNotFound('Node ID [%s] not found.' % (_id))

        return dbNode

    def getNodeByIp(self, session: Session, ip: str) -> Node:
        """
        Raises:
            NodeNotFound
        """

        self._logger.debug('Retrieving node by IP [%s]' % (ip))

        try:
            return session.query(Node).join(Nic).filter(Nic.ip == ip).one()
        except NoResultFound:
            raise NodeNotFound(
                'Node with IP address [%s] not found.' % (ip))

    def getNodeList(self, session: Session,
                    softwareProfile: Optional[str] = None,
                    tags: Optional[Tags] = None) -> List[Node]:
        """
        Get sorted list of nodes from the db.

        Raises:
            SoftwareProfileNotFound
        """

        self._logger.debug('getNodeList()')

        if softwareProfile:
            dbSoftwareProfile = \
                self._softwareProfilesDbHandler.getSoftwareProfile(
                    session, softwareProfile)

            return dbSoftwareProfile.nodes

        searchspec = []

        if tags:
            for name, value in tags.items():
                if value:
                    #
                    # Match both name and value
                    #
                    searchspec.append(and_(
                        Node.tags.any(name=name),
                        Node.tags.any(value=value)
                    ))
                else:
                    #
                    # Match name only
                    #
                    searchspec.append(Node.tags.any(name=name))

        return session.query(Node).filter(
            or_(*searchspec)).order_by(Node.name).all()

    def getNodeListByNodeStateAndSoftwareProfileName(
            self, session: Session, nodeState: str,
            softwareProfileName: str) -> List[Node]:
        """
        Get list of nodes from the db.
        """

        self._logger.debug(
            'Retrieving nodes with state [%s] from software'
            ' profile [%s]' % (nodeState, softwareProfileName))

        return session.query(Node).join(SoftwareProfile).filter(and_(
            SoftwareProfile.name == softwareProfileName,
            Node.state == nodeState)).all()

    def getNodesByNodeState(self, session: Session, state: str) -> List[Node]:
        return session.query(Node).filter(Node.state == state).all()

    def getNodesByMac(self, session: Session, usedMacList: List[str]) \
            -> List[Node]:
        if not usedMacList:
            return []

        return session.query(Node).join(Nic).filter(
            Nic.mac.in_(usedMacList)).all()

    def build_node_filterspec(self, nodespec: str) -> List[str]:
        filter_spec = []

        for nodespec_token in nodespec.split(','):
            # Convert shell-style wildcards into SQL wildcards
            if '*' in nodespec_token or '?' in nodespec_token:
                filter_spec.append(
                    nodespec_token.replace('*', '%').replace('?', '_'))

                continue

            if '.' not in nodespec_token:
                filter_spec.append(nodespec_token)
                filter_spec.append(nodespec_token + '.%')

                continue

            # Add nodespec "AS IS"
            filter_spec.append(nodespec_token)

        return filter_spec

    def expand_nodespec(self, session: Session, nodespec: str,
                        include_installer: Optional[bool] = True) \
            -> List[Node]:
        """
        Expand command-line nodespec (ie. "compute*") to list of nodes
        """

        return self.getNodesByNameFilter(
            session,
            self.build_node_filterspec(nodespec),
            include_installer=include_installer
        )
