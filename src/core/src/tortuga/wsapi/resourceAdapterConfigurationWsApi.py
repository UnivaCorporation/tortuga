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
from .tortugaWsApi import TortugaWsApi


class ResourceAdapterConfigurationWsApi(TortugaWsApi):
    """Resource adapter configuration client web service API"""

    def create(self, resadapter_name, name, configuration):
        url = 'v1/resourceadapters/{0}/profile/{1}'.format(
            resadapter_name, name)

        postdata = json.dumps(dict(configuration=configuration))

        try:
            _, responseDict = self.sendSessionRequest(
                url, method='POST', data=postdata)

            return responseDict
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def get(self, resadapter_name, name):
        """Get resource adapter configuration"""

        url = 'v1/resourceadapters/{0}/profile/{1}'.format(
            resadapter_name, name)

        try:
            _, responseDict = self.sendSessionRequest(url)

            return responseDict
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def get_profile_names(self, resadapter_name):
        url = 'v1/resourceadapters/{0}/profile/'.format(resadapter_name)

        try:
            _, responseDict = self.sendSessionRequest(url, method='GET')
            return responseDict
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def delete(self, resadapter_name, name):
        url = 'v1/resourceadapters/{0}/profile/{1}'.format(
            resadapter_name, name)

        try:
            _, responseDict = self.sendSessionRequest(url, method='DELETE')

            return responseDict
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)

    def update(self, resadapter_name, name, configuration):
        url = 'v1/resourceadapters/{0}/profile/{1}'.format(
            resadapter_name, name)

        postdata = json.dumps(configuration)

        try:
            _, responseDict = self.sendSessionRequest(
                url, method='PUT', data=postdata)

            return responseDict
        except TortugaException:
            raise
        except Exception as ex:
            raise TortugaException(exception=ex)
