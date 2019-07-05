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

# pylint: disable=too-few-public-methods

from marshmallow import fields, post_dump
from marshmallow_sqlalchemy import ModelSchema

from tortuga.db.models.component import Component as ComponentModel
from tortuga.db.models.hardwareProfile import \
    HardwareProfile as HardwareProfileModel
from tortuga.db.models.hardwareProfileTag import \
    HardwareProfileTag as HardwareProfileTagModel
from tortuga.db.models.kit import Kit as KitModel
from tortuga.db.models.network import Network as NetworkModel
from tortuga.db.models.networkDevice \
    import NetworkDevice as NetworkDeviceModel
from tortuga.db.models.nic import Nic as NicModel
from tortuga.db.models.node import Node as NodeModel
from tortuga.db.models.nodeTag import NodeTag as NodeTagModel
from tortuga.db.models.operatingSystem import \
    OperatingSystem as OperatingSystemModel
from tortuga.db.models.operatingSystemFamily import \
    OperatingSystemFamily as OperatingSystemFamilyModel
from tortuga.db.models.osComponent import OsComponent as OsComponentModel
from tortuga.db.models.osFamilyComponent import \
    OsFamilyComponent as OsFamilyComponentModel
from tortuga.db.models.resourceAdapter import \
    ResourceAdapter as ResourceAdapterModel
from tortuga.db.models.resourceAdapterConfig import \
    ResourceAdapterConfig as ResourceAdapterConfigModel
from tortuga.db.models.softwareProfile import \
    SoftwareProfile as SoftwareProfileModel
from tortuga.db.models.softwareProfileTag import \
    SoftwareProfileTag as SoftwareProfileTagModel
from tortuga.db.models.admin import Admin as AdminModel
from tortuga.db.models.resourceAdapterSetting import \
    ResourceAdapterSetting as ResourceAdapterSettingModel
from tortuga.db.models.instanceMapping import \
    InstanceMapping as InstanceMappingModel
from tortuga.db.models.instanceMetadata import \
    InstanceMetadata as InstanceMetadataModel


class AdminSchema(ModelSchema):
    class Meta:
        model = AdminModel


class OperatingSystemSchema(ModelSchema):
    family = fields.Nested('OperatingSystemFamilySchema',
                           exclude=('children',))

    class Meta:
        model = OperatingSystemModel


class OperatingSystemFamilySchema(ModelSchema):
    class Meta:
        model = OperatingSystemFamilyModel


class NetworkDeviceSchema(ModelSchema):
    class Meta:
        model = NetworkDeviceModel


class NicSchema(ModelSchema):
    network = fields.Nested('NetworkSchema',
                            exclude=('nics', 'hardwareprofilenetworks'))
    networkdevice = fields.Nested('NetworkDeviceSchema',
                                  only=('id', 'name'))

    class Meta:
        model = NicModel


class NetworkSchema(ModelSchema):
    nics = fields.Nested('NicSchema', many=True, exclude=('networks',))

    class Meta:
        model = NetworkModel


class KitSchema(ModelSchema):
    class Meta:
        model = KitModel


class OsComponentSchema(ModelSchema):
    os = fields.Nested('OperatingSystem')

    class Meta:
        model = OsComponentModel


class OsFamilyComponentSchema(ModelSchema):
    family = fields.Nested('OperatingSystemFamilySchema')

    class Meta:
        model = OsFamilyComponentModel


class ComponentSchema(ModelSchema):
    kit = fields.Nested('KitSchema', exclude=('components',))
    os = fields.Nested('OperatingSystemSchema')

    class Meta:
        model = ComponentModel


class ResourceAdapterConfigSettingSchema(ModelSchema):
    class Meta:
        model = ResourceAdapterSettingModel


class ResourceAdapterConfigSchema(ModelSchema):
    resourceadapter = fields.Nested('ResourceAdapterSchema',
                                    only=('id', 'name', 'settings'))
    admin = fields.Nested('AdminSchema', only=('id', 'username'))
    configuration = fields.Nested('ResourceAdapterConfigSettingSchema',
                                  only=('id', 'key', 'value'), many=True)

    class Meta:
        model = ResourceAdapterConfigModel


class ResourceAdapterSchema(ModelSchema):
    credentials = fields.Nested('ResourceAdapterConfigSchema')
    settings = fields.Method('get_settings', dump_only=True)

    class Meta:
        model = ResourceAdapterModel

    def get_settings(self, obj: ResourceAdapterModel):
        settings = {}
        for k, v in obj.settings.items():
            settings[k] = v.schema().dump(v).data
        return settings


class InstanceMetadataSchema(ModelSchema):
    instance = fields.Nested(
        'InstanceMappingSchema',
        exclude=('instance_metadata', 'resource_adapter_configuration')
    )

    class Meta:
        model = InstanceMetadataModel


class InstanceMappingSchema(ModelSchema):
    instance_metadata = fields.Nested('InstanceMetadataSchema', many=True)
    resource_adapter_configuration = \
        fields.Nested('ResourceAdapterConfigSchema')
    node = fields.Nested('NodeSchema', only=('id', 'name'))

    class Meta:
        model = InstanceMappingModel


class NodeTagSchema(ModelSchema):
    class Meta:
        model = NodeTagModel


class NodeSchema(ModelSchema):
    softwareprofile = fields.Nested('SoftwareProfileSchema',
                                    only=('id', 'name', 'metadata'))
    hardwareprofile = fields.Nested(
        'HardwareProfileSchema',
        only=('id', 'name', 'resourceadapter'),
        exclude=('resourceadapter.hardwareprofiles',
                 'resourceadapter.credentials',
                 'resourceadapter.kit')
    )

    nics = fields.Nested('NicSchema', many=True, exclude=('node',))

    vcpus = fields.Integer(default=1)

    tags = fields.Nested('NodeTagSchema',
                         only=('id', 'name', 'value'), many=True)

    instance = fields.Nested('InstanceMappingSchema')

    # Post process tags so that the schema serialization matches our
    # standard object serialization
    @post_dump(pass_many=True, pass_original=True)
    def fixTags(self, in_data, many, original):
        if isinstance(in_data, list):
            for i in range(0, len(in_data)):
                tagFunc = getattr(original[i], "getTags", None)
                if callable(tagFunc):
                    in_data[i]['tags'] = tagFunc()
        else:
            tagFunc = getattr(original, "getTags", None)
            if callable(tagFunc):
                in_data['tags'] = tagFunc()
        return in_data

    class Meta:
        model = NodeModel


class SoftwareProfileTagSchema(ModelSchema):
    class Meta:
        model = SoftwareProfileTagModel


class SoftwareProfileSchema(ModelSchema):
    nodes = fields.Nested('NodeSchema', many=True,
                          exclude=('softwareprofile',))

    components = fields.Nested('ComponentSchema', many=True,
                               exclude=('softwareprofiles',))

    hardwareprofiles = fields.Nested('HardwareProfileSchema',
                                     only=('id', 'name', 'resourceadapter'),
                                     many=True)

    os = fields.Nested('OperatingSystemSchema')

    tags = fields.Nested('SoftwareProfileTagSchema',
                         only=('id', 'name', 'value'), many=True)

    metadata = fields.Dict()

    class Meta:
        model = SoftwareProfileModel


class HardwareProfileTagSchema(ModelSchema):
    class Meta:
        model = HardwareProfileTagModel


class HardwareProfileSchema(ModelSchema):
    nodes = fields.Nested('NodeSchema', many=True,
                          exclude=('hardwareprofile',))

    mappedsoftwareprofiles = fields.Nested('SoftwareProfileSchema',
                                           only=('id', 'name'), many=True)

    tags = fields.Nested('HardwareProfileTagSchema',
                         only=('id', 'name', 'value'), many=True)

    resourceadapter = fields.Nested('ResourceAdapterSchema',
                                    only=('id', 'name'))

    class Meta:
        model = HardwareProfileModel
