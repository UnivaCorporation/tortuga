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

from typing import Optional, Iterable

from tortuga.exceptions.tortugaException import TortugaException

from .tortugaWsApi import TortugaWsApi


class MetadataWsApi(TortugaWsApi):
    def list(self, *, filter_key: Optional[str] = None,
             filter_value: Optional[str] = None):
        url = 'metadata/'

        query_string = process_query_string(
            ('filter_key', 'filter_value'),
            filter_key=filter_key,
            filter_value=filter_value,
        )

        if query_string:
            url += '?' + query_string

        try:
            return self.get(url)
        except TortugaException:
            raise
        except Exception as exc:
            raise TortugaException(exception=exc)

    def deleteMetadata(self, *, filter_key: Optional[str] = None,
                       filter_value: Optional[str] = None):
        url = 'metadata/'

        query_string = process_query_string(
            ('filter_key', 'filter_value'),
            filter_key=filter_key,
            filter_value=filter_value,
        )
        if query_string:
            url += '?' + query_string

        try:
            return self.delete(url)
        except TortugaException:
            raise
        except Exception as exc:
            raise TortugaException(exception=exc)


def process_query_string(keys: Iterable[str], **kwargs) -> Optional[str]:
    qs = {}

    value = kwargs.get('filter_key')
    if value is not None:
        qs['filter_key'] = value

    value = kwargs.get('filter_value')
    if value is not None:
        qs['filter_value'] = value

    if not qs:
        return None

    return '&'.join(['%s=%s' % (key, value) for key, value in qs.items()])
