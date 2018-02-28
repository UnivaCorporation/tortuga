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


class AuthPrincipal(object):
    def __init__(self, name, password=None, attributeDict=None):
        self.__name = name
        self.__password = password
        self.__attributeDict = attributeDict or {}

    def getName(self):
        """ Return the principals name """
        return self.__name

    def getPassword(self):
        """ Return the principals password """
        return self.__password

    def getAttributes(self):
        """ Return dictionary of principal's attributes """
        return self.__attributeDict
