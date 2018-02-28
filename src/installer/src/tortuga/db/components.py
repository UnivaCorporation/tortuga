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

from tortuga.kit.utils import format_component_descriptor


class Components(object):

    def __init__(self, name=None, version=None, description=None,
                 kitId=None):
        self.name = name
        self.version = version
        self.description = description
        self.kitId = kitId

    def __repr__(self):
        return format_component_descriptor(self.name, self.version)
