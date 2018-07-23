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

import argparse

import yaml

from tortuga.exceptions.invalidCliRequest import InvalidCliRequest
from tortuga.objects.osInfo import OsInfo


class ParseOperatingSystemArgAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        osValues = values.split('-', 3)

        if len(osValues) != 3:
            raise InvalidCliRequest(
                _('Error: Incorrect operating system specification.'
                  '\n\n--os argument should be in'
                  ' OSNAME-OSVERSION-OSARCH format'))

        name = osValues[0]
        version = osValues[1]
        arch = osValues[2]

        setattr(namespace, 'osInfo', OsInfo(name, version, arch))


class FilterTagsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        tags = []

        vals = values.split('=', 1)

        if len(vals) == 2:
            tags.append((vals[0], vals[1]))
        else:
            tags.append((vals[0],))

        current_tags = getattr(namespace, self.dest) \
            if hasattr(namespace, self.dest) else None
        if current_tags is None:
            setattr(namespace, self.dest, tags)
        else:
            current_tags.extend(tags)


def pretty_print(data):
    """
    Outputs data as nicely formatted YAML.

    :param data: A Python data structure

    """
    print(yaml.safe_dump(data, default_flow_style=False))
