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


def getRuleApi(username=None, password=None):
    """
    Creates an object that derives from RuleApiInterface
    Only WS API is supported for now.
    """

    from tortuga.wsapi import ruleWsApi
    api = ruleWsApi.RuleWsApi(username, password)

    return api
