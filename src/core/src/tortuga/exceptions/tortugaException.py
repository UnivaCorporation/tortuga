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

from tortuga.utility import tortugaStatus


class TortugaException(Exception):
    """
    Base tortuga exception class.

    Usage:
        TortugaException(errorMessage, errorCode)
        TortugaException(args=errorMessage)
        TortugaException(exception=exceptionObject)
    """

    def __init__(self, error='', code=tortugaStatus.TORTUGA_ERROR,
                 **kwargs):
        args = error
        if args == "":
            args = kwargs.get('args', "")
        ex = kwargs.get('exception', None)
        if ex is not None and isinstance(ex, Exception):
            exArgs = "%s" % (ex)
            if args == "":
                args = exArgs
            else:
                args = "%s (%s)" % (args, exArgs)

        super(TortugaException, self).__init__(args)

        self._code = code

    def getArgs(self):
        """ Return exception arguments. """
        return self.args

    def getErrorCode(self):
        """ Return erro code. """
        return self._code

    def getErrorMessage(self):
        """ Return exception error. """
        return "%s" % (self.args)

    def getClassName(self):
        """ Return class name. """
        return "%s" % (self.__class__.__name__)
