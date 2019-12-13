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
import time
from typing import List

from celery.schedules import crontab
from sqlalchemy.orm.session import Session
from tortuga.os_utility.tortugaSubprocess import executeCommand

from tortuga.exceptions.nodeNotFound import NodeNotFound
from tortuga.tasks.celery import app
from tortuga.db.nodesDbHandler import NodesDbHandler
from tortuga.db.models.node import Node


logger = logging.getLogger(__name__)


class NodePingReply:
    def __init__(self, name: str, reply: bool, response_time: float):
        self.name: str = name
        self.reply: bool = reply
        self.response_time: float = response_time


class NodePinger:
    def ping_all_nodes(self) -> List[NodePingReply]:
        raise NotImplementedError()


class McollectiveNodePinger(NodePinger):
    _command = 'mco ping'

    def ping_all_nodes(self) -> List[NodePingReply]:
        p = executeCommand(self._command)

        replies: List[NodePingReply] = []
        for line in p.getStdOut().decode().splitlines():
            #
            # A typical ping response from the mco ping command looks like
            # this:
            #
            # execd-01-hioqz    time=52.88 ms
            #
            parts = re.split(r"\s+", line.strip())
            if len(parts) != 3:
                continue
            if not parts[1].startswith("time="):
                continue
            replies.append(
                NodePingReply(
                    name=parts[0],
                    reply=True,
                    response_time=float(parts[1].replace("time=", ""))
                )
            )

        return replies


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    #
    # Run the node pinter every 5 minutes
    #
    logger.info(
        'Setting-up periodic task to run every 5 minutes: node_pinger')
    sender.add_periodic_task(
        crontab(minute="*/5"),
        node_pinger.s(),
    )


@app.task()
def node_pinger():
    """
    Ping all known nodes and update their lastUpdate timestamps. This gives
    us a way to determine if there are nodes that have not been responsive
    for a certain period of time.

    """
    np: NodePinger = McollectiveNodePinger()
    replies: List[NodePingReply] = np.ping_all_nodes()

    node_api: NodesDbHandler = NodesDbHandler()
    sess: Session = app.dbm.openSession()

    for r in replies:
        #
        # First try to get the node by name directly...
        #
        try:
            nodes: List[Node] = [node_api.getNode(sess, r.name)]
        #
        # ...then try to get the node using a wildcard, in case the node
        # name returned was not fully qualified
        #
        except NodeNotFound:
            nodes: List[Node] = node_api.expand_nodespec(sess,
                                                         "{}*".format(r.name))
        #
        # Still no nodes found? Log a warning and continue.
        #
        if len(nodes) == 0:
            logger.warning(
                'Node pinger could not find node: {}, skipping'.format(r.name)
            )
            continue

        #
        # Set the lastUpdate timestamp
        #
        for node in nodes:
            node.lastUpdate = time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        sess.commit()
