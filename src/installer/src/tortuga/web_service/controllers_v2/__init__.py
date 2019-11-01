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

import cherrypy

from tortuga.kit.registry import get_all_kit_installers
from .registry import register_ws_controller, get_all_ws_controllers
from .events import EventController
from .hardwareprofiles import HardwareProfileController
from .nodes import NodeController
from .resourcerequests import ResourceRequestController
from .softwareprofiles import SoftwareProfileController
from .tags import TagController


#
# Register web service controllers
#
register_ws_controller(EventController)
register_ws_controller(HardwareProfileController)
register_ws_controller(NodeController)
register_ws_controller(ResourceRequestController)
register_ws_controller(SoftwareProfileController)
register_ws_controller(TagController)


def setup_routes():
    """
    Used to setup RESTFul resources.

    """
    #
    # Ensure all kits are loaded, and their web services are registered
    #
    for kit_installer_class in get_all_kit_installers():
        kit_installer = kit_installer_class()
        kit_installer.register_web_service_controllers()
        kit_installer.register_event_listeners()

    dispatcher = cherrypy.dispatch.RoutesDispatcher()
    dispatcher.mapper.explicit = False
    for controller_class in get_all_ws_controllers():
        controller = controller_class()
        for action in controller.actions:
            dispatcher.connect(
                action['name'],
                action['path'],
                action=action['action'],
                controller=controller,
                conditions=dict(method=action['method'])
            )
    return dispatcher
