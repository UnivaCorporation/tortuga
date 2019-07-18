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

from typing import Dict, Type

from marshmallow import fields

from tortuga.types.base import BaseType, BaseTypeSchema
from ..exceptions import ResourceRequestNotFoundError


#
# Dictionary, storing registered resource_request classes
#
RESOURCE_REQUEST_TYPES: Dict[str, Type['BaseResourceRequest']] = {}


def get_resource_request_class(name: str) -> Type['BaseResourceRequest']:
    """
    Gets the resource request class for a specified resource_request name.

    :param str name:                      the name of the resource
                                          request
    :return BaseResource_request:         the class for the requested
                                          resource request
    :raises ResourceRequestNotFoundError: if the resource_request class is
                                          not found

    """
    try:
        return RESOURCE_REQUEST_TYPES[name]
    except KeyError:
        raise ResourceRequestNotFoundError()


class ResourceRequestMeta(type):
    """
    Metaclass for resource request types.

    The purpose of this metaclass is to register resource request types
    so that they can easily be looked-up by name.

    """
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)

        #
        # Don't attempt to load the base installer
        #
        if name == 'base':
            return

        RESOURCE_REQUEST_TYPES[cls.name] = cls


class BaseResourceRequestSchema(BaseTypeSchema,
                                metaclass=ResourceRequestMeta):
    name: fields.Field = fields.String(dump_only=True)
    timestamp: fields.Field = fields.DateTime()


class BaseResourceRequest(BaseType):
    type = 'resource-request'
    schema_class = BaseResourceRequestSchema
    
    name: str = 'base-resource-request'


