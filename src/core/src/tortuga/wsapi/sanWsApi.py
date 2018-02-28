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

from tortuga.exceptions.tortugaException import TortugaException
from tortuga.objects.volume import Volume
from .tortugaWsApi import TortugaWsApi


class SanWsApi(TortugaWsApi):
    """
    SAN WS API class.
    """

    def getVolumeList(self):
        """
        Get volume list.

            Returns:
                [volumes]
            Throws:
                TortugaException
        """

        url = 'v1/san/volumes'

        try:
            _, responseDict = self.sendSessionRequest(url)

            return Volume.getListFromDict(responseDict)
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def updateVolume(self, volume, shared):
        """Add a volume to the system"""

        url = 'v1/san/volumes/%s/%s' % (volume, shared)

        try:
            self.sendSessionRequest(url, method='PUT')
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def addVolume(self, storageAdapter, size, nameFormat='*', shared=False):
        """Add a volume to the system"""

        url = 'v1/san/volumes/%s/%s/%s/%s' % (
            storageAdapter, size, nameFormat, shared)

        try:
            _, responseDict = self.sendSessionRequest(url, method='POST')

            return Volume.getFromDict(responseDict.get(Volume.ROOT_TAG))
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def deleteVolume(self, volume, force=False): \
            # pylint: disable=unused-argument
        """Delete a volume from the system"""

        url = 'v1/san/volumes/%s' % (volume)

        try:
            self.sendSessionRequest(url, method='DELETE')
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)
