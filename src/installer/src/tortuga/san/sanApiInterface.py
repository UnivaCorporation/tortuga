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

from tortuga.exceptions.abstractMethod import AbstractMethod


class SanApiInterface(object):
    '''
    This is the interface spec for the san api.
    '''

    def addVolume(self, storageAdapter, size, nameFormat='*',
                  persistent=False): \
            # pylint: disable=no-self-use,unused-argument
        raise AbstractMethod('addVolume() must be implemented in the'
                             ' concrete API class')

    def deleteVolume(self, volume, force=False): \
            # pylint: disable=no-self-use,unused-argument
        raise AbstractMethod('deleteVolume() must be implemented in the'
                             ' concrete API class')

    def getVolumeList(self): \
            # pylint: disable=no-self-use
        raise AbstractMethod('getVolumeList() must be implemented in the'
                             ' concrete API class')

    def updateVolume(self, volume, persistent): \
            # pylint: disable=no-self-use,unused-argument
        raise AbstractMethod('updateVolume() must be implemented in the'
                             ' concrete API class')
