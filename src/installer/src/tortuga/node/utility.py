import json
import threading
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from tortuga.db.models.node import Node
from tortuga.db.models.nodeRequest import NodeRequest
from tortuga.db.models.softwareProfile import SoftwareProfile
from tortuga.db.nodesDbHandler import NodesDbHandler
from tortuga.db.softwareProfilesDbHandler import SoftwareProfilesDbHandler
from tortuga.exceptions.operationFailed import OperationFailed


class SoftwareProfileNodeCountValidator:
    def __init__(self):
        self._master_lock: threading.Lock = threading.Lock()
        self._software_profile_locks: Dict[str, threading.Lock] = {}

    def _get_lock(self, swp_name: str) -> threading.Lock:
        """
        Gets a lock for a specific software profile and returns it. Note
        that this does not acquire the lock, but just looks it up and
        returns it.

        :param str swp_name: the software profile name

        :return threading.Lock: the lock

        """
        try:
            return self._software_profile_locks[swp_name]

        except KeyError:
            return self._create_lock(swp_name)

    def _create_lock(self, swp_name: str) -> threading.Lock:
        """
        Creates a lock for a specific software profile and returns it. Note
        that this does not acquire the lock.

        :param str swp_name: the software profile name

        :return threading.Lock: the lock

        """
        self._master_lock.acquire()
        try:
            lck = self._software_profile_locks[swp_name]

        except KeyError:
            lck = threading.Lock()
            self._software_profile_locks[swp_name] = lck

        finally:
            self._master_lock.release()

        return lck

    def validate_add_count(self, sess: Session, swp_name: str,
                           count: int):
        """
        Validates an add nodes request for the node count. This call
        takes into account any other add operations currently in progress.

        :param Session sess: a database session
        :param str swp_name: the name of the software profile
        :param int count:    the number of nodes to add

        :raises OperationFailed:

        """
        lck = self._get_lock(swp_name)
        lck.acquire()
        #
        # Wrap the actual function logic so that we can ensure that all
        # locks are removed in a clean fashion
        #
        try:
            self._validate_add_count(sess, swp_name, count)

        finally:
            lck.release()

    def _validate_add_count(self, sess: Session, swp_name: str,
                            count: int):
        """
        See validate_add_count.

        """
        swp_api = SoftwareProfilesDbHandler()
        swp = swp_api.getSoftwareProfile(sess, swp_name)

        if swp.maxNodes <= 0:
            return
        current_count = len(swp.nodes)
        request_count = self._count_current_node_requests(sess, swp)

        if current_count + request_count + count > swp.maxNodes:
            raise OperationFailed(
                'Request to add {} node(s) exceeds software profile'
                ' limit of {} nodes'.format(count, swp.maxNodes)
            )

    def _count_current_node_requests(self, sess: Session,
                                     swp: SoftwareProfile) -> int:
        """
        Returns a count of nodes in pending add node requests.

        :param Session sess:        a database session
        :param SoftwareProfile swp: a software profile

        :return int: the count of nodes currently pending

        """
        count = 0

        for nr in sess.query(NodeRequest).filter(
                NodeRequest.action == 'ADD').filter(
                NodeRequest.state == 'pending'):
            req = json.loads(nr.request)
            if req.get('softwareProfile', None) != swp.name:
                continue
            count += int(req.get('count', 0))

        return count

    def validate_remove_count(self, sess: Session, nodespec: str,
                              force: bool = False):
        """
        Validates a removal request.

        :param Session sess: a database session
        :param str nodespec: the node spec of nodes to remove
        :param bool force:   whether or not this is a force operation

        :raise OperationFailed:

        """
        locks: Dict[str, threading.Lock] = {}
        #
        # Wrap the actual function logic so that we can ensure that all
        # locks are removed in a clean fashion
        #
        try:
            self._validate_remove_count(sess, locks, nodespec, force)

        finally:
            for lck in locks.values():
                lck.release()

    def _validate_remove_count(self, sess: Session,
                               locks: Dict[str, threading.Lock],
                               nodespec: str, force: bool = False):
        """
        See validate_remove_count.

        """
        nodes = self._get_nodes_from_nodespec(sess, nodespec)
        swp_counts: Dict[SoftwareProfile, int] = {}

        #
        # Count how many nodes are being deleted for each software profile
        #
        for node in nodes:
            swp = node.softwareprofile

            if swp.name not in locks.keys():
                locks[swp.name] = self._get_lock(swp.name)
                locks[swp.name].acquire()

            if swp not in swp_counts:
                swp_counts[swp] = 0
            swp_counts[swp] += 1

        #
        # Validate each software profile to ensure the deletion is permitted
        #
        for swp, num_nodes_deleted in swp_counts.items():
            if swp.lockedState == 'HardLocked':
                raise OperationFailed(
                    'Nodes cannot be deleted from hard locked software '
                    'profile [{}]'.format(swp.name)
                )
            if swp.lockedState == 'SoftLocked' and not force:
                raise OperationFailed(
                    'Nodes cannot be deleted from soft locked software '
                    'profile [{}]'.format(swp.name)
                )
            #
            # if there is no minimum, then no need to check anything else
            #
            if not swp.minNodes:
                continue
            #
            # Ensure the proposed deletion keeps things above the minimum
            #
            if len(swp.nodes) - num_nodes_deleted < swp.minNodes:
                raise OperationFailed(
                    'Software profile [{}] requires minimum of {} nodes; '
                    'denied request to delete {} node(s)'.format(
                        swp.name, swp.minNodes, num_nodes_deleted
                    )
                )

    def _get_nodes_from_nodespec(self, sess: Session,
                                 nodespec: str) -> List[Node]:
        """
        Given a node spec, return the list of nodes matching the spec.

        :param Session sess: a database session
        :param str nodespec: a node spec

        :return List[Node]:  a list of nodes matching the spec

        """
        node_api = NodesDbHandler()
        nodes = node_api.expand_nodespec(sess, nodespec,
                                         include_installer=False)
        if not nodes:
            return []

        return nodes


