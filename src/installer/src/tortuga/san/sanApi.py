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

from tortuga.utility.tortugaApi import TortugaApi
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.exceptions.unsupportedOperation import UnsupportedOperation
from tortuga.san.san import San
from tortuga.objects.tortugaObject import TortugaObjectList


class SanApi(TortugaApi):
    """
    SAN API class.
    """

    def __init__(self):
        super(SanApi, self).__init__()

        self._san = San()

    def addVolume(self, storageAdapter, size, nameFormat='*', shared=False):
        """Add a volume to the system"""

        try:
            # The api only allows for the addition of persistent volumes
            return self._san.addVolume(
                storageAdapter, size, nameFormat, persistent=True,
                shared=shared)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % (ex))
            raise TortugaException(exception=ex)

    def deleteVolume(self, volume, force=False): \
            # pylint: disable=unused-argument
        """
        Delete a volume from the system

        Raises:
            UnsupportedOperation
            VolumeDoesNotExist
        """

        try:
            # This will throw an exception if the volume is not valid
            self.__getPersistentVolume(volume)

            # We are deleting a persistent volume so force must be True
            return self._san.deleteVolume(volume, force=True)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % (ex))
            raise TortugaException(exception=ex)

    def getVolumeList(self):
        """
        Get volume list..

            Returns:
                list of volumes
            Throws:
                TortugaException
        """

        try:
            return TortugaObjectList([volume
                                      for volume in self._san.getVolumeList()
                                      if volume.getPersistent()])
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def updateVolume(self, volume, shared):
        """
        Update an existing volume.

        Throws:
            UnsupportedOperation
            VolumeDoesNotExist
            TortugaException
        """

        try:
            # Can only update persistent volumes through this interface
            # This will throw an exception if the volume is not valid
            self.__getPersistentVolume(volume)

            self._san.updateVolume(
                volume, newPersistent=True, newShared=shared)
        except TortugaException as ex:
            raise
        except Exception as ex:
            self.getLogger().exception('%s' % ex)
            raise TortugaException(exception=ex)

    def __getPersistentVolume(self, volume):
        """
        Raises:
            VolumeDoesNotExist
            UnsupportedOperation
        """

        vol = self._san.getVolume(volume)

        if not vol.getPersistent():
            raise UnsupportedOperation(
                'Volume [%s] is not persistent' % (volume))

        return vol
