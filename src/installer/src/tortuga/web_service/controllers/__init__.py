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

from .registry import register_ws_controller, get_all_ws_controllers

from .addHostController import AddHostController
from .adminController import AdminController
from .applicationMonitorController import ApplicationMonitorController
from .authController import AuthController
from .hardwareProfileController import HardwareProfileController
from .kitController import KitController
from .networkController import NetworkController
from .nodeController import NodeController
from .parameterController import ParameterController
from .resourceAdapterConfigurationController import \
    ResourceAdapterConfigurationController
from .ruleController import RuleController
from .softwareProfileController import SoftwareProfileController
from .tagController import TagController
from .updateController import UpdateController
from tortuga.kit.loader import load_kits
from tortuga.kit.registry import get_all_kit_installers


register_ws_controller(AddHostController)
register_ws_controller(AdminController)
register_ws_controller(ApplicationMonitorController)
register_ws_controller(AuthController)
register_ws_controller(HardwareProfileController)
register_ws_controller(KitController)
register_ws_controller(NetworkController)
register_ws_controller(NodeController)
register_ws_controller(ParameterController)
register_ws_controller(ResourceAdapterConfigurationController)
register_ws_controller(RuleController)
register_ws_controller(SoftwareProfileController)
register_ws_controller(TagController)
register_ws_controller(UpdateController)
