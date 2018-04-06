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

import logging
import urllib.request, urllib.error, urllib.parse
import json
import urllib.parse
import http.client
import ssl

from tortuga.exceptions.urlErrorException import UrlErrorException
from tortuga.exceptions.httpErrorException import HttpErrorException
from tortuga.web_client import exceptionMapper


class SessionManager:
    """
    Class for session management.
    """

    def __init__(self):
        """ Initialize session manager instance. """
        self._sessionCookie = None
        self._host = None
        self._logger = logging.getLogger(
            'tortuga.web_client.%s' % (self.__class__.__name__))
        self._logger.addHandler(logging.NullHandler())
        self._username = None
        self._password = None

    def setHost(self, host):
        """ Set host. """
        self._host = host

    def hasSession(self):
        """ Return true if we have session established. """
        return self._sessionCookie is not None

    def establishSession(self, url, username, password,
                         selector='/v1/auth/login'):
        """
        Establish session

        Raises:
            UrlErrorException
        """

        self._host = url
        self._username = username
        self._password = password

        self._logger.debug(
            'Establishing session for user [%s]'
            ' (url: %s, selector: %s)' % (username, url, selector))

        data = {
            'username': username,
            'password': password,
        }

        try:
            response, _ = self.sendRequest(
                url='%s%s' % (url, selector),
                method='POST',
                data=json.dumps(data))
        except urllib.error.URLError as ex:
            self._logger.exception('Establish session raised exception')

            raise UrlErrorException(exception=ex)

        self._sessionCookie = response.headers['Set-Cookie']

        exceptionMapper.checkStatus(response.headers)

    def _response_handler(self, response): \
            # pylint: disable=no-self-use
        # 'checkStatus()' raises TortugaException-derived exception if API
        # status code is not 'TORTUGA_OK' (success)
        exceptionMapper.checkStatus(response.headers)

        # Otherwise, return the parsed JSON response body
        responseDict = json.loads(response.read().decode()) \
            if 'Content-Length' in response.headers and \
            int(response.headers['Content-Length']) else {}

        return response, responseDict

    def sendRequest(self, url, method='GET',
                    contentType='application/json', data=None,
                    acceptType='application/json'):
        """
        Send HTTP request without cookies

        Raises:
            HttpErrorException
            UrlErrorException
        """

        u = urllib.parse.urlparse(url)

        if not u.scheme and not u.netloc:
            url = '%s/%s' % (self._host, url)

        self._logger.debug(
            'sendRequest(): url=[{}] method=[{}] data=[{}]'.format(url,
                                                                   method,
                                                                   data)
        )

        request = urllib.request.Request(
            url, data=data.encode() if data else None, method=method)

        if method != 'GET':
            # do not send 'Content-Type' header for GET requests
            request.add_header('Content-Type', contentType)

        if acceptType:
            request.add_header('Accept', acceptType)

        if self._sessionCookie is not None:
            request.add_header('Cookie', self._sessionCookie)

        # Check if SSL certificate verification is available
        if not hasattr(ssl, 'create_default_context'):
            ssl_handler = urllib.request.HTTPSHandler()
        else:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            ssl_handler = urllib.request.HTTPSHandler(context=ctx)

        try:
            opener = urllib.request.build_opener(ssl_handler)

            response = opener.open(request)

            return self._response_handler(response)
        except urllib.error.HTTPError as ex:
            if ex.code == http.client.UNAUTHORIZED and self._host is not None:
                if u.path.endswith('/auth/login'):
                    raise HttpErrorException('Authentication error')

                self.establishSession(
                    self._host, self._username, self._password)

                return self.sendRequest(url, method, contentType, data)

            if ex.code == http.client.INTERNAL_SERVER_ERROR:
                raise HttpErrorException('Internal server error')

            if ex.code == http.client.BAD_REQUEST:
                self._response_handler(ex)

                raise HttpErrorException('Invalid request (bad arguments?)')

            return self._response_handler(ex)
        except urllib.error.URLError as ex:
            # For example, "connection refused", et al.
            raise UrlErrorException(exception=ex)


def createSession():
    return SessionManager()
