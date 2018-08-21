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

import json
from logging import getLogger
from typing import Optional, Type, Union

import marshmallow
import requests

from tortuga.config.configManager import ConfigManager


logger = getLogger(__name__)


class RequestError(Exception):
    """
    An exception that is raised if we get a non 2xx response from the
    API server.

    """
    def __init__(self, *args, status_code: int,
                 data: Optional[Union[dict, list]] = None,
                 **kwargs):
        """
        Initializer.

        :param args:
        :param int status_code:                  the HTTP status code
        :param Optional[Union[dict, list]] data: the response data, if any
        :param kwargs:

        """
        self.status_code = status_code
        self.data = data
        super().__init__(*args, **kwargs)


class InvalidResponse(Exception):
    """
    An exception that is raised if we get a response from the server that we
    cannot validate.

    """
    pass


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

        self._cm = ConfigManager()

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
                self._requests_kwargs['verify'] = self._cm.getCaBundle()
                logger.debug('Using CA path: {}'.format(
                    self._cm.getCaBundle()))

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

    def process_response(
            self,
            response: requests.Response,
            response_schema: Optional[Type[marshmallow.Schema]] = None,
            error_schema: Optional[Type[marshmallow.Schema]] = None
            ) -> Optional[Union[list, dict]]:
        """
        Process the response, parsing out the data and handling
        errors/exceptions as required.

        :param requests.Response response:        the response from the
                                                  request
        :param Optional[Type[marshmallow.Schema]] response_schema:
                    validate the response against a schema?
        :param Optional[Type[marshmallow.Schema]] error_schema:
                    validate the error payload against a schema?

        :return Optional[Union[list, dict]]: the response
        
        :raises RequestError:   if the a non 2xx status code is returned
        :raises InvalidResponse if the response or error cannot be properly
                                validated

        """
        #
        # Check for 2xx status code. If it isn't a 2xx status code, then
        # treat it as an error, and handle appropriately
        #
        if round(response.status_code / 100) != 2:
            self.process_error_response(response)

        #
        # Attempt to get JSON from the response, otherwise None
        #
        data = None
        try:
            data = response.json()

        except Exception:
            pass

        logger.debug('Response Payload: {}'.format(json.dumps(data)))

        #
        # If a response schema is provided, then validate the response against
        # the schema.
        #
        if response_schema:
            try:
                data = response_schema().load(data).data

            except marshmallow.ValidationError:
                raise InvalidResponse('ERROR: Invalid Server Response')

        return data

    def process_error_response(
            self,
            error_response: requests.Response,
            error_schema: Optional[Type[marshmallow.Schema]] = None):
        """
        Process the response as an error.

        :param requests.Response error_response:
                    the response from the request
        :param Optional[Type[marshmallow.Schema]] error_schema:
                    validate the error payload against a schema?

        :raises RequestError:   if the a non 2xx status code is returned
        :raises InvalidResponse if the response or error cannot be properly
                                validated

        """
        logger.debug('ERROR Code: {}'.format(error_response.status_code))

        #
        # Attempt to get JSON data from the error response
        #
        data = None
        try:
            data = error_response.json()

        except Exception:
            pass

        logger.debug('ERROR Payload: {}'.format(json.dumps(data)))

        #
        # If an error schema is provided, then validate the error data
        # against the schema
        #
        if error_schema:
            try:
                data = error_schema().load(data).data

            except marshmallow.ValidationError:
                raise InvalidResponse('ERROR: Invalid Server Response')

        raise RequestError(
            "ERROR: API Request Error {}".format(error_response.status_code),
            status_code=error_response.status_code,
            data=data
        )

    def get(self,
            path: str,
            response_schema: Optional[Type[marshmallow.Schema]] = None,
            error_schema: Optional[Type[marshmallow.Schema]] = None
            ) -> Union[list, dict]:
        """
        Performs a GET request on the specified path. It is assumed the
        result is JSON, and it is decoded as such.

        :param str path: the API path to get from
        :param Optional[Type[marshmallow.Schema]] response_schema:
                         validate the response against a schema?
        :param Optional[Type[marshmallow.Schema]] error_schema:
                         validate the error payload against a schema?

        :return Union[list, dict]: the response, JSON decoded

        """
        url = self.build_url(path)
        logger.debug('GET: {}'.format(url))

        result = requests.get(
            url,
            **self.get_requests_kwargs()
        )

        return self.process_response(result, response_schema, error_schema)

    def post(self,
             path: str,
             data: Optional[dict] = None,
             response_schema: Optional[Type[marshmallow.Schema]] = None,
             error_schema: Optional[Type[marshmallow.Schema]] = None
             ) -> Optional[dict]:
        """
        Post data to a specified path (API endpoint). Data will automatically
        be encoded as JSON.

        :param str path:  the API path to post to
        :param dict data: the data to post
        :param Optional[Type[marshmallow.Schema]] response_schema:
                          validate the response against a schema?
        :param Optional[Type[marshmallow.Schema]] error_schema:
                          validate the error payload against a schema?

        :return dict: the response of the request

        """
        url = self.build_url(path)
        logger.debug('POST: {}'.format(url))

        result = requests.post(
            url,
            json=data,
            **self.get_requests_kwargs()
        )

        return self.process_response(result, response_schema, error_schema)

    def put(self,
            path: str,
            data: Optional[dict] = None,
            response_schema: Optional[Type[marshmallow.Schema]] = None,
            error_schema: Optional[Type[marshmallow.Schema]] = None
            ) -> Optional[dict]:
        """
        Put data to a specified path (API endpoint). Data will automatically
        be encoded as JSON.

        :param str path:  the API path to put to
        :param dict data: the data to post
        :param Optional[Type[marshmallow.Schema]] response_schema:
                          validate the response against a schema?
        :param Optional[Type[marshmallow.Schema]] error_schema:
                          validate the error payload against a schema?

        :return dict: the response of the request

        """
        url = self.build_url(path)
        logger.debug('PUT: {}'.format(url))

        result = requests.put(
            url,
            json=data,
            **self.get_requests_kwargs()
        )

        return self.process_response(result, response_schema, error_schema)

    def delete(self,
               path: str,
               response_schema: Optional[Type[marshmallow.Schema]] = None,
               error_schema: Optional[Type[marshmallow.Schema]] = None
               ) -> Optional[dict]:
        """
        Delete from the specified path.

        :param str path: the path to delete
        :param Optional[Type[marshmallow.Schema]] response_schema:
                         validate the response against a schema?
        :param Optional[Type[marshmallow.Schema]] error_schema:
                         validate the error payload against a schema?

        :return dict : the result of the delete

        """
        url = self.build_url(path)
        logger.debug('DELETE: {}'.format(url))

        result = requests.delete(
            url,
            **self.get_requests_kwargs()
        )

        return self.process_response(result, response_schema, error_schema)

    def patch(self,
              path: str, data: Optional[dict] = None,
              response_schema: Optional[Type[marshmallow.Schema]] = None,
              error_schema: Optional[Type[marshmallow.Schema]] = None
              ) -> Optional[dict]:
        """
        Patch data to a specified path (API endpoint). Data will automatically
        be encoded as JSON.

        :param str path:  the API path to put to
        :param dict data: the data to post
        :param Optional[Type[marshmallow.Schema]] response_schema:
                          validate the response against a schema?
        :param Optional[Type[marshmallow.Schema]] error_schema:
                          validate the error payload against a schema?

        :return dict: the response of the request

        """
        url = self.build_url(path)
        logger.debug('PATCH: {}'.format(url))

        result = requests.patch(
            url,
            json=data,
            **self.get_requests_kwargs()
        )

        return self.process_response(result, response_schema, error_schema)
