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

import pkgutil
import tortuga.resourceAdapter
from tortuga.exceptions.resourceNotFound import ResourceNotFound


def find_resource_adapters():
    subclasses = []

    def look_for_subclass(module_name):
        module = __import__(module_name)

        d = module.__dict__
        for m in module_name.split('.')[1:]:
            d = d[m].__dict__

        for key, entry in d.items():
            if key == tortuga.resourceAdapter.resourceAdapter.\
                    ResourceAdapter.__name__:
                continue

            try:
                if issubclass(entry, tortuga.resourceAdapter.
                              resourceAdapter.ResourceAdapter):
                    subclasses.append(entry)
            except TypeError:
                continue

    for _, modulename, _ in pkgutil.walk_packages(
            tortuga.resourceAdapter.__path__):
        look_for_subclass('tortuga.resourceAdapter.{0}'.format(modulename))

    return subclasses


def getResourceAdapterClass(adapter_name):
    for adapter in find_resource_adapters():
        if adapter.__adaptername__ == adapter_name:
            return adapter

    raise ResourceNotFound(
        'Unable to find resource adapter [{0}]'.format(adapter_name))


def getApi(adapter_name):
    return getResourceAdapterClass(adapter_name)()
