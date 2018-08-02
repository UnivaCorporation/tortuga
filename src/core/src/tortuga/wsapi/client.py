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

from logging import getLogger
from typing import Optional, Union
import os
import requests

logger = getLogger(__name__)


CA_BUNDLE_PATH = '/etc/pki/tls/certs/ca-bundle.crt'


class RestApiClient:
    """
    A generic REST API Client class.

    """
    def __init__(self, username: Optional[str] = None,
                 password: Optional[str] = None,
                 baseurl: Optional[str] = None,
                 verify: bool = True):

        if baseurl.endswith('/'):
            baseurl = baseurl[:-1]

        self.baseurl = baseurl
        self.username = username
        self.password = password
        self.verify = verify

        self._requests_kwargs = None

        if not verify:
            logger.warning('SSL verification turned off')

    def get_requests_kwargs(self) -> dict:
        #
        # Cache the base kwargs
        #
        if self._requests_kwargs is None:
            #
            # Authentication
            #
            self._requests_kwargs = {
                'auth': (self.username, self.password)
            }
            #
            # SSL cert verification
            #
            if self.verify:
                if os.path.exists(CA_BUNDLE_PATH):
                    self._requests_kwargs['verify'] = CA_BUNDLE_PATH
                    logger.debug('Using CA bundle: {}'.format(CA_BUNDLE_PATH))
                else:
                    logger.debug('Using built-in CA bundle')
            else:
                self._requests_kwargs['verify'] = False

        return self._requests_kwargs

    def build_url(self, path: str) -> str:
        """
        Given a path, returns a fully qualified URL.

        :param str path: the path for which to build the URL

        :return str: the full URL

        """
        if not path.startswith('/'):
            path = '/{}'.format(path)

        return '{}{}'.format(self.baseurl, path)

    def process_response(self, response: requests.Response
                         ) -> Optional[Union[list, dict]]:
        try:
            return response.json()

        except ValueError:
            response.raise_for_status()

            return None

    def get(self, path: str) -> Union[list, dict]:
        """
        Performs a GET request on the specified path. It is assumed the
        result is JSON, and it is decoded as such.

        :param str path: the API path to get from

        :return Union[list, dict]: the response, JSON decoded

        """
        url = self.build_url(path)
        logger.debug('GET: {}'.format(url))

        result = requests.get(
            url,
            **self.get_requests_kwargs()
        )

        return self.process_response(result)

    def post(self, path: str, data: Optional[dict] = None) -> Optional[dict]:
        """
        Post data to a specified path (API endpoint). Data will automatically
        be encoded as JSON.

        :param str path:  the API path to post to
        :param dict data: the data to post

        :return dict: the response of the request

        """
        url = self.build_url(path)
        logger.debug('POST: {}'.format(url))

        result = requests.post(
            url,
            json=data,
            **self.get_requests_kwargs()
        )

        return self.process_response(result)

    def put(self, path: str, data: Optional[dict] = None) -> Optional[dict]:
        """
        Put data to a specified path (API endpoint). Data will automatically
        be encoded as JSON.

        :param str path:  the API path to put to
        :param dict data: the data to post

        :return dict: the response of the request

        """
        url = self.build_url(path)
        logger.debug('PUT: {}'.format(url))

        result = requests.put(
            url,
            json=data,
            **self.get_requests_kwargs()
        )

        return self.process_response(result)

    def delete(self, path: str) -> Optional[dict]:
        """
        Delete from the specified path.

        :param str path: the path to delete

        :return dict : the result of the delete

        """
        url = self.build_url(path)
        logger.debug('DELETE: {}'.format(url))

        result = requests.delete(
            url,
            **self.get_requests_kwargs()
        )

        return self.process_response(result)

    def patch(self, path: str, data: Optional[dict] = None) -> Optional[dict]:
        """
        Patch data to a specified path (API endpoint). Data will automatically
        be encoded as JSON.

        :param str path:  the API path to put to
        :param dict data: the data to post

        :return dict: the response of the request

        """
        url = self.build_url(path)
        logger.debug('PATCH: {}'.format(url))

        result = requests.patch(
            url,
            json=data,
            **self.get_requests_kwargs()
        )

        return self.process_response(result)
