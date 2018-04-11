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

# pylint: disable=no-member

import json

from tortuga.exceptions.tortugaException import TortugaException
from tortuga.objects.addHostStatus import AddHostStatus

from .tortugaWsApi import TortugaWsApi


class AddHostWsApi(TortugaWsApi):
    """
    AddHost WS API class.
    """
    def addNodes(self, addNodesRequest):
        """
        Main entry point into adding nodes.

            Returns:
                addhost session
            Throws:
                RuleNotFound
                TortugaException
        """

        try:
            _, responseDict = self.sendSessionRequest(
                url='v1/nodes',
                method='POST',
                data=json.dumps({'node': addNodesRequest}))

            return responseDict.get('addHostSession')
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def getStatus(self, session=None, startMessage=0, getNodes=False):
        """
        Get the status of addhost...if session is non-none get info for that
        session only.  Startmessage controls the number of removed from
        the start of the server side message list.  If getNodes is true
        also include the nodes for this session.

        Returns:
            AddHostStatus object
        Throws:
            TortugaException
        """

        url = 'v1/addhost/%s/status' % (session)

        # Add query parameters
        url += '?startMessage={0}&getNodes={1}'.format(
            startMessage, str(getNodes))

        try:
            _, responseDict = self.sendSessionRequest(url)

            return AddHostStatus.getFromDict(responseDict.get("addhoststatus"))
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)
