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

from .mapper_admins import AdminsTableMapper
from .mapper_components import ComponentsTableMapper
from .mapper_global_params import GlobalParamsTableMapper
from .mapper_hardware_profiles import (HardwareProfilesTableMapper,
                                       HardwareProfileNetworksTableMapper,
                                       HardwareProfileTagsTableMapper)
from .mapper_kits import KitsTableMapper, KitSourcesTableMapper
from .mapper_networks import (NetworkDevicesTableMapper, NetworksTableMapper,
                              NicsTableMapper)
from .mapper_nodes import (NodesTableMapper, NodeRequestsTableMapper,
                           NodeTagsTableMapper)
from .mapper_os import (OperatingSystemsTableMapper, OsComponentsTableMapper,
                        OperatingSystemsFamiliesTableMapper,
                        OsFamilyComponentsTableMapper)
from .mapper_packages import PackagesTableMapper
from .mapper_partitions import PartitionsTableMapper
from .mapper_resource_adapters import (ResourceAdaptersTableMapper,
                                       ResourceAdapterCredentialsTableMapper)
from .mapper_software_profiles import (SoftwareProfilesTableMapper,
                                       SoftwareProfileComponentsTableMapper,
                                       SoftwareProfileKitSourcesTableMapper,
                                       SoftwareProfileTagsTableMapper)
from .mapper_software_uses_hardware import SoftwareUsesHardwareTableMapper
from .mapper_tags import TagsTableMapper
from .registry import register_table_mapper, get_all_table_mappers


#
# Register table mappers. Note: order matters here, as tables have
# dependencies.
#
register_table_mapper(NetworksTableMapper)
register_table_mapper(KitsTableMapper)
register_table_mapper(KitSourcesTableMapper)
register_table_mapper(SoftwareProfileKitSourcesTableMapper)
register_table_mapper(AdminsTableMapper)
register_table_mapper(NetworkDevicesTableMapper)
register_table_mapper(TagsTableMapper)
register_table_mapper(NodeTagsTableMapper)
register_table_mapper(SoftwareProfileTagsTableMapper)
register_table_mapper(HardwareProfileTagsTableMapper)
register_table_mapper(HardwareProfileNetworksTableMapper)
register_table_mapper(HardwareProfilesTableMapper)
register_table_mapper(SoftwareProfileComponentsTableMapper)
register_table_mapper(SoftwareUsesHardwareTableMapper)
register_table_mapper(SoftwareProfilesTableMapper)
register_table_mapper(GlobalParamsTableMapper)
register_table_mapper(NicsTableMapper)
register_table_mapper(NodesTableMapper)
register_table_mapper(OperatingSystemsFamiliesTableMapper)
register_table_mapper(OperatingSystemsTableMapper)
register_table_mapper(OsComponentsTableMapper)
register_table_mapper(OsFamilyComponentsTableMapper)
register_table_mapper(ComponentsTableMapper)
register_table_mapper(PackagesTableMapper)
register_table_mapper(PartitionsTableMapper)
register_table_mapper(ResourceAdaptersTableMapper)
register_table_mapper(NodeRequestsTableMapper)
register_table_mapper(ResourceAdapterCredentialsTableMapper)
