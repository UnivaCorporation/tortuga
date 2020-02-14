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

from tortuga.resources.manager import ResourceRequestStoreManager
from tortuga.resources.types import (BaseResourceRequest,
                                     get_resource_request_class)
from .base import Controller


class ResourceRequestController(Controller):
    """
    ResourceRequest web service controller class.

    """
    name = 'resourcerequests'
    type_store = ResourceRequestStoreManager.get()
    methods = ['GET', 'POST', 'PUT', 'DELETE']

    def unmarshall(self, obj_dict: dict) -> BaseResourceRequest:
        #
        # Since different request types have different classes, we have
        # to lookup the class type before unmarshalling
        #
        resource_request_class = get_resource_request_class(
            obj_dict['resource_type'])
        scheam_class = resource_request_class.get_schema_class()
        unmarshalled = scheam_class().load(obj_dict)
        return resource_request_class(**unmarshalled.data)
