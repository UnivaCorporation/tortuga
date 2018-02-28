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

class KitSources(object): \
        # pylint: disable=too-few-public-methods

    def __init__(self, url=None, description=None):
        self.url = url
        self.description = description

    def __repr__(self):
        return '<KitSources(description=[%s], url=[%s])>' % (
            self.description, self.url)
