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

from sqlalchemy import Sequence
from sqlalchemy import (Table, Boolean, Column, Index, ForeignKey, Integer,
                        String)
from sqlalchemy.orm import mapper, relation

from .mapper import TableMapper
from ..admins import Admins
from ..components import Components
from ..hardwareProfiles import HardwareProfiles
from ..kitSources import KitSources
from ..nodes import Nodes
from ..operatingSystems import OperatingSystems
from ..packages import Packages
from ..partitions import Partitions
from ..softwareProfileAdmins import SoftwareProfileAdmins
from ..softwareProfileComponents import SoftwareProfileComponents
from ..softwareProfileKitSources import SoftwareProfileKitSources
from ..softwareProfiles import SoftwareProfiles
from ..softwareProfileTags import SoftwareProfileTags
from ..tags import Tags


class SoftwareProfilesTableMapper(TableMapper):
    def map(self, db_manager):
        backend_opts = db_manager.get_backend_opts()

        softwareprofiles_table = Table(
            'SoftwareProfiles',
            db_manager.metadata,
            Column('id', Integer, Sequence('softwareprofiles_id_seq'),
                   primary_key=True),
            Column('name', String(45), nullable=False, unique=True),
            Column('description', String(255)),
            Column('kernel', String(255)),
            Column('kernelParams', String(512)),
            Column('initrd', String(255)),
            Column('osId', Integer, ForeignKey('OperatingSystems.id'),
                   nullable=False),
            Column('type', String(20), nullable=False),
            Column('minNodes', Integer),
            Column('isIdle', Boolean, nullable=False, default=False),
            **backend_opts
        )

        softwareprofileadmins_table = Table(
            'SoftwareProfileAdmins',
            db_manager.metadata,
            Column('softwareProfileId', Integer,
                   ForeignKey('SoftwareProfiles.id'), nullable=False,
                   primary_key=True),
            Column('adminId', Integer, ForeignKey('Admins.id'),
                   nullable=False, primary_key=True),
            **backend_opts
        )

        Index('SoftwareProfileAdmins_softwareProfileId',
              softwareprofileadmins_table.c.softwareProfileId)
        Index('SoftwareProfileAdmins_adminId',
              softwareprofileadmins_table.c.adminId)

        mapper(SoftwareProfileAdmins, softwareprofileadmins_table)

        tbl2 = db_manager.getMetadataTable('HardwareProfiles')

        # Register table with db manager.
        mapper(SoftwareProfiles, softwareprofiles_table, properties={
            'admins': relation(
                Admins, backref='softwareprofiles',
                secondary=softwareprofileadmins_table),
            'components': relation(
                Components,
                secondary=db_manager.getMetadataTable(
                    'SoftwareProfileComponents'), backref='softwareprofiles'),
            'nodes': relation(Nodes, backref='softwareprofile'),
            'os': relation(
                OperatingSystems, lazy=False),
            'packages': relation(
                Packages, cascade="all,delete-orphan",
                backref='softwareprofiles'),
            'partitions': relation(Partitions, cascade="all,delete-orphan"),
            'hardwareprofiles': relation(
                HardwareProfiles,
                secondary=db_manager.
                    getMetadataTable('SoftwareUsesHardware'),
                lazy=False, backref='mappedsoftwareprofiles'),
            'hwprofileswithidle': relation(
                HardwareProfiles,
                primaryjoin=softwareprofiles_table.c.id ==
                            tbl2.c.idleSoftwareProfileId,
                backref='idlesoftwareprofile'
            ),
            'children': relation(
                HardwareProfiles,
                primaryjoin=softwareprofiles_table.c.id ==
                            tbl2.c.hypervisorSoftwareProfileId,
                backref='hypervisor'),
            'kitsources': relation(
                KitSources,
                secondary=db_manager.getMetadataTable(
                    'SoftwareProfileKitSources'),
                backref='softwareprofiles'),
            'tags': relation(
                Tags,
                primaryjoin=softwareprofiles_table.c.id ==
                            db_manager.metadata.tables[
                                'softwareprofile_tags'].c.softwareprofile_id,
                secondary=db_manager.metadata.tables[
                    'softwareprofile_tags'],
                backref='softwareprofiles'),
        })


class SoftwareProfileComponentsTableMapper(TableMapper):
    def map(self, db_manager):
        backend_opts = db_manager.get_backend_opts()

        softwareprofilecomponents_table = Table(
            'SoftwareProfileComponents',
            db_manager.metadata,
            Column('softwareProfileId', Integer,
                   ForeignKey('SoftwareProfiles.id'), index=True,
                   primary_key=True),
            Column('componentId', Integer, ForeignKey('Components.id'),
                   index=True, primary_key=True),
            **backend_opts
        )

        mapper(SoftwareProfileComponents, softwareprofilecomponents_table)


class SoftwareProfileKitSourcesTableMapper(TableMapper):
    def map(self, db_manager):
        backend_opts = db_manager.get_backend_opts()

        software_profile_kit_sources_table = Table(
            'SoftwareProfileKitSources',
            db_manager.metadata,
            Column('id', Integer, primary_key=True),
            Column('softwareProfileId', Integer,
                   ForeignKey('SoftwareProfiles.id')),
            Column('kitSourceId', Integer, ForeignKey('KitSources.id')),
            **backend_opts
        )

        mapper(SoftwareProfileKitSources, software_profile_kit_sources_table)


class SoftwareProfileTagsTableMapper(TableMapper):
    def map(self, db_manager):
        backend_opts = db_manager.get_backend_opts()

        softwareprofile_tags_table = Table(
            'softwareprofile_tags',
            db_manager.metadata,
            Column('id', Integer, primary_key=True),
            Column('softwareprofile_id', Integer,
                   ForeignKey('SoftwareProfiles.id')),
            Column('tag_id', Integer, ForeignKey('tags.id'), nullable=False),
            **backend_opts)

        mapper(SoftwareProfileTags, softwareprofile_tags_table)
