from marshmallow_sqlalchemy import ModelSchema
from tortuga.db.models.node import Node as NodeModel
from tortuga.db.models.softwareProfile \
    import SoftwareProfile as SoftwareProfileModel
from tortuga.db.models.hardwareProfile \
    import HardwareProfile as HardwareProfileModel


class NodeSchema(ModelSchema):
    class Meta:
        model = NodeModel


class SoftwareProfileSchema(ModelSchema):
    class Meta:
        model = SoftwareProfileModel


class HardwareProfileSchema(ModelSchema):
    class Meta:
        model = HardwareProfileModel
