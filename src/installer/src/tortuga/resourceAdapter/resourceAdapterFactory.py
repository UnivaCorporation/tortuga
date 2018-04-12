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

from tortuga.exceptions.resourceNotFound import ResourceNotFound
import tortuga.resourceAdapter


def find_resourceadapters():
    """
    Finds all resource adapter classes.

    :return List[ResourceAdapter]: a list of all resource adapter classes

    """
    subclasses = []

    def look_for_subclass(module_name):
        module = __import__(module_name)

        d = module.__dict__
        for m in module_name.split('.')[1:]:
            d = d[m].__dict__

        for key, entry in d.items():
            if key == tortuga.resourceAdapter.resourceAdapter.ResourceAdapter.__name__:
                continue

            try:
                if issubclass(entry, tortuga.resourceAdapter.resourceAdapter.ResourceAdapter):
                    subclasses.append(entry)
            except TypeError:
                continue

    for _, modulename, _ in pkgutil.walk_packages(
            tortuga.resourceAdapter.__path__):
        look_for_subclass('tortuga.resourceAdapter.{0}'.format(modulename))

    return subclasses


def get_resourceadapter_class(adapter_name: str):
    """
    Gets the resource adapter class for the given resource adapter name.

    :param adapter_name:      the name of the resource adapter
    :return ResourceAdatper:  a resource adapter class
    :raises ResourceNotFound:

    """
    for adapter in find_resourceadapters():
        if adapter.__adaptername__ == adapter_name:
            return adapter

    raise ResourceNotFound(
        'Unable to find resource adapter [{0}]'.format(adapter_name))


def get_api(adapter_name: str):
    """
    Gets an instantiated resource adapter class for the given resource
    adapter name.

    :param adapter_name:      the name of the resource adapter
    :return: ResourceAdapter: a resource adapter instance
    :raises ResourceNotFound:

    """
    return get_resourceadapter_class(adapter_name)()
