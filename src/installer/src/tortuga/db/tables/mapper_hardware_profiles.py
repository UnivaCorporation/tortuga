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

from sqlalchemy import Table, Boolean, Column, ForeignKey, Index, Integer, Sequence, String
from sqlalchemy.orm import mapper, relation

from .mapper import TableMapper
from ..admins import Admins
from ..hardwareProfiles import HardwareProfiles
from ..hardwareProfileAdmins import HardwareProfileAdmins
from ..hardwareProfileNetworks import HardwareProfileNetworks
from ..hardwareProfileProvisioningNics import HardwareProfileProvisioningNics
from ..hardwareProfileTags import HardwareProfileTags
from ..networks import Networks
from ..networkDevices import NetworkDevices
from ..nics import Nics
from ..nodes import Nodes
from ..resourceAdapters import ResourceAdapters
from ..tags import Tags


class HardwareProfilesTableMapper(TableMapper):
    def map(self, db_manager):
        backend_opts = db_manager.get_backend_opts()

        hardwareprofiles_table = Table(
            'HardwareProfiles',
            db_manager.metadata,
            Column('id', Integer, Sequence('hardwareprofiles_id_seq'),
                   primary_key=True),
            Column('name', String(45), nullable=False, unique=True),
            Column('description', String(255)),
            Column('nameFormat', String(45)),
            Column('installType', String(20), nullable=False,
                   default='package'),
            Column('kernel', String(255)),
            Column('kernelParams', String(512)),
            Column('initrd', String(255)),
            Column('softwareOverrideAllowed', Boolean, nullable=False,
                   default=True),
            Column('idleSoftwareProfileId', Integer,
                   ForeignKey('SoftwareProfiles.id')),
            Column('location', String(45), default='local'),
            Column('localBootParams', String(255)),
            Column('hypervisorSoftwareProfileId', Integer,
                   ForeignKey('SoftwareProfiles.id')),
            Column('maxUnits', Integer, default=0),
            Column('resourceAdapterId', Integer,
                   ForeignKey('ResourceAdapters.id')),
            Column('bcastEnabled', Boolean, nullable=False, default=True),
            Column('mcastEnabled', Boolean, nullable=False, default=True),
            Column('cost', Integer, default=0),
            **backend_opts
        )

        # HardwareProfileAdmins

        hardwareprofileadmins_table = Table(
            'HardwareProfileAdmins',
            db_manager.metadata,
            Column(
                'hardwareProfileId', Integer,
                ForeignKey('HardwareProfiles.id'), primary_key=True),
            Column(
                'adminId', Integer, ForeignKey('Admins.id'),
                primary_key=True),
            **backend_opts
        )

        Index('HardwareProfileAdmins_hardwareProfileId',
              hardwareprofileadmins_table.c.hardwareProfileId)

        Index('HardwareProfileAdmins_adminId',
              hardwareprofileadmins_table.c.adminId)

        mapper(HardwareProfileAdmins, hardwareprofileadmins_table)

        # HardwareProfileProvisioningNics

        hardwareprofileprovisioningnics_table = Table(
            'HardwareProfileProvisioningNics',
            db_manager.metadata,
            Column('hardwareProfileId', Integer,
                   ForeignKey('HardwareProfiles.id'), nullable=False,
                   primary_key=True),
            Column('nicId', Integer, ForeignKey('Nics.id'),
                   nullable=False, primary_key=True),
            **backend_opts
        )

        Index(
            'HardwareProfileProvisioningNics_hardwareProfileId',
            hardwareprofileprovisioningnics_table.c.hardwareProfileId)

        Index(
            'HardwareProfileProvisioningNics_nicId',
            hardwareprofileprovisioningnics_table.c.nicId)

        mapper(
            HardwareProfileProvisioningNics,
            hardwareprofileprovisioningnics_table, properties={
                'nic': relation(Nics),
                'hardwareprofile': relation(HardwareProfiles),
            }
        )

        # Register table with db manager.
        mapper(
            HardwareProfiles, hardwareprofiles_table, properties={
                'admins': relation(
                    Admins, secondary=hardwareprofileadmins_table,
                    backref='hardwareprofiles'),
                'hardwareprofilenetworks': relation(
                    HardwareProfileNetworks, backref='hardwareprofile',
                    cascade="all,delete-orphan"),
                'nodes': relation(Nodes, backref='hardwareprofile'),
                'nics': relation(
                    Nics, secondary=hardwareprofileprovisioningnics_table,
                    lazy=False),
                'resourceadapter': relation(
                    ResourceAdapters, backref='hardwareprofiles'),
                'tags': relation(
                    Tags,
                    primaryjoin=hardwareprofiles_table.c.id ==
                                db_manager.metadata.tables[
                                    'hardwareprofile_tags'].c.hardwareprofile_id,
                    secondary=db_manager.metadata.tables[
                        'hardwareprofile_tags'],
                    backref='hardwareprofiles'),
            }
        )


class HardwareProfileNetworksTableMapper(TableMapper):
    def map(self, db_manager):
        backend_opts = db_manager.get_backend_opts()

        hardwareprofilenetworks_table = Table(
            'HardwareProfileNetworks',
            db_manager.metadata,
            Column('hardwareProfileId', Integer,
                   ForeignKey('HardwareProfiles.id'), primary_key=True),
            Column('networkId', Integer, ForeignKey('Networks.id'),
                   primary_key=True, index=True),
            Column('networkDeviceId', Integer,
                   ForeignKey('NetworkDevices.id'), primary_key=True,
                   index=True),
            **backend_opts
        )

        mapper(HardwareProfileNetworks, hardwareprofilenetworks_table,
               properties={
                   'networkdevice': relation(
                       NetworkDevices, lazy=False),
                   'network': relation(
                       Networks, backref="hardwareprofilenetworks",
                       lazy=False)
               })


class HardwareProfileTagsTableMapper(TableMapper):
    def map(self, db_manager):
        backend_opts = db_manager.get_backend_opts()

        hardwareprofile_tags_table = Table(
            'hardwareprofile_tags',
            db_manager.metadata,
            Column('id', Integer, primary_key=True),
            Column('hardwareprofile_id', Integer,
                   ForeignKey('HardwareProfiles.id')),
            Column('tag_id', Integer, ForeignKey('tags.id'), nullable=False),
            **backend_opts)

        mapper(HardwareProfileTags, hardwareprofile_tags_table)
