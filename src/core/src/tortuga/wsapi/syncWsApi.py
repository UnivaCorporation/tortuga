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
from typing import Optional, Union

from tortuga.exceptions.tortugaException import TortugaException

from .tortugaWsApi import TortugaWsApi


class SyncWsApi(TortugaWsApi):
    """Cluster sync WS API class"""

    def scheduleClusterUpdate(self, updateReason: Optional[Union[str, None]] = None):
        """Schedule cluster update.

            Returns:
                None
            Throws:
                UserNotAuthorized
                TortugaException
        """

        url = 'updates/cluster'

        postdata = {}

        if updateReason:
            postdata['reason'] = updateReason

        try:
            self.post(url, postdata)

        except TortugaException:
            raise

        except Exception as ex:
            raise TortugaException(exception=ex)

    def getUpdateStatus(self):
        """Return cluster update status

            Returns:
                Boolean - True if cluster update is currently running
            Throws:
                TortugaException
        """

        url = 'updates/cluster'

        try:
            responseDict = self.get(url)

            return str2bool(responseDict.get('running'))

        except TortugaException:
            raise

        except Exception as ex:
            raise TortugaException(exception=ex)
