"""Rename Nodes table to nodes

Revision ID: c39f7655419a
Revises: 
Create Date: 2018-04-14 14:27:57.420306

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c39f7655419a'
down_revision = None
branch_labels = None
depends_on = None


old_tables = [
    ('Admins', 'admins'),
    ('OsComponents', 'os_components'),
    ('Components', 'components'),
    ('OsFamilyComponents', 'osfamily_components'),
    ('GlobalParameters', 'global_parameters'),
    ('Partitions', 'partitions'),
    ('HardwareProfileAdmins', 'hardwareprofile_admins'),
    ('ResourceAdapters', 'resourceadapters'),
    ('HardwareProfileNetworks', 'hardwareprofile_networks'),
    ('SoftwareProfileAdmins', 'softwarprofile_admins'),
    ('HardwareProfileProvisioningNics', 'hardwareprofile_provisioning_nics'),
    ('SoftwareProfileComponents', 'softwareprofile_components'),
    ('HardwareProfiles', 'hardwareprofiles'),
    ('SoftwareProfileKitSources', 'softwareprofile_kitsources'),
    ('KitSources', 'kitsources'),
    ('SoftwareProfiles', 'softwareprofiles'),
    ('Kits', 'kits'),
    ('SoftwareUsesHardware', 'software_uses_hardware'),
    ('NetworkDevices', 'networkdevices'),
    ('Networks', 'networks'),
    ('Nics', 'nics'),
    ('NodeRequests', 'node_requests'),
    ('resourceadaptercredentials', 'resource_adapter_credentials'),
    ('Nodes', 'nodes'),
    ('OperatingSystems', 'operatingsystems'),
    ('OperatingSystemsFamilies', 'operatingsystemsfamilies'),
]


def rename_table(original_name, new_name):
    op.rename_table(original_name, original_name + '_new')
    op.rename_table(original_name + '_new', new_name)


def upgrade():
    for original_name, new_name in old_tables:
        rename_table(original_name, new_name)


def downgrade():
    for original_name, new_name in old_tables:
        rename_table(new_name, original_name)
