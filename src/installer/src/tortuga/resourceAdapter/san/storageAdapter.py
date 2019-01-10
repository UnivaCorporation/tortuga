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

# pylint: disable=no-self-use,no-name-in-module

import re
import logging
from tortuga.exceptions.unsupportedOperation import UnsupportedOperation
from tortuga.logging import STORAGE_ADAPTER_NAMESPACE
from tortuga.os_utility.tortugaSubprocess import executeCommand
from tortuga.exceptions.internalError import InternalError


class StorageAdapter(object):
    '''
    This is the base class for all storage adapters to derive from.
    The default actions simply print a debug message to show that the
    subclass did not implement the action.
    '''

    def __init__(self):
        self._logger = logging.getLogger(STORAGE_ADAPTER_NAMESPACE)

    def allocateVolume(self, sizeInMB, nameFormat=None):
        '''Allocate a volume of the given size'''
        self.__trace(sizeInMB, nameFormat)

    def deleteVolume(self, volume):
        '''Delete the given volume'''
        self.__trace(volume)

    def connectVolume(self, volume, targetHost, persistent):
        '''Connect a given volume to a particular node'''
        self.__trace(volume, targetHost, persistent)

    def disconnectVolume(self, volume, targetHost, device, persistent):
        '''Disconnect a given volume from a particular node'''
        self.__trace(volume, targetHost, device, persistent)

    def authorizeNode(self, nodeName, volume):
        '''Authorize a node to connect to a given volume'''
        self.__trace(nodeName, volume)

    def deauthorizeNode(self, nodeName, volume):
        '''Deauthorized a node to connect to a given volume'''
        self.__trace(nodeName, volume)

    def supportsCheckpoint(self):
        '''Indicates whether or not a drive can be checkpointed'''
        return False

    def checkpointDrive(self, volume):
        '''Checkpoint the given node'''
        # By default raise unsupported operation
        raise UnsupportedOperation(
            'Volume %s does not support checkpointing' % (volume))

    def revertDriveToCheckpoint(self, volume):
        '''Revert the given node to its checkpoint'''
        # By default raise unsupported operation
        raise UnsupportedOperation(
            'Volume %s does not support checkpointing' % (volume))

    def __trace(self, *pargs, **kargs):
        import traceback
        stack = traceback.extract_stack()
        funcname = stack[-2][2]

        self._logger.debug(
            '-- (pass) %s::%s %s %s' % (
                self.__class__.__name__, funcname, pargs, kargs))

    def parseConfig(self, resourceAdapterConfig):
        if resourceAdapterConfig:
            configList = resourceAdapterConfig.split(';')
            configDict = {}
            for config in configList:
                key, val = config.split('=')
                configDict[key] = val
            return configDict
        else:
            return None

    def getInitiatorName(self, target):
        '''Gets the iSCSI Initiator name of the specified target host/IP'''

        cmd = 'ssh root@%s cat /etc/iscsi/initiatorname.iscsi' % (target)

        stdout = executeCommand(cmd).getStdOut()

        pattern = re.compile(
            r'^\s*InitiatorName=["\']?([^"\' ]+)[^\'"]?', re.M)

        match = pattern.search(stdout)

        if not match:
            raise InternalError(
                'Target [%s] unknown iSCSI initiator name' % (target))

        initiator = match.group(1).strip()

        self._logger.debug(
            'Target [%s] iSCSI initiator name: [%s]' % (target, initiator))

        return initiator
