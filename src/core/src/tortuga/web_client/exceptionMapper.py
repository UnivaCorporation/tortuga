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
from tortuga.exceptions.tortugaException import TortugaException


def checkStatus(httpHeaders):
    """ Map tortuga status code into appropriate exception. """

    code = httpHeaders.get('Tortuga-Status-Code', None)

    msg = httpHeaders.get('Tortuga-Status-Message', 'Internal Error')

    if code is None or code == str(tortugaStatus.TORTUGA_OK):
        return

    if int(code) in tortugaStatus.exceptionMap:
        # Exception string is value of the form 'x.y.z'
        # where 'x.y' is tortuga module, and 'z' class in that module

        exStr = tortugaStatus.exceptionMap.get(int(code))
        exClass = exStr.split('.')[-1]  # 'z' in 'x.y.z'
        exModule = '.'.join(exStr.split('.')[:-1])  # 'x.y' in 'x.y.z'

        temp_ = __import__(
            'tortuga.{0}'.format(exModule), globals(), locals(),
            [exClass], 0)

        _Exception = getattr(temp_, exClass)

        raise _Exception(msg)

    raise TortugaException(msg)
