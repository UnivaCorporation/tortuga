import cherrypy

from tortuga.kit.loader import load_kits
from tortuga.kit.registry import get_all_kit_installers
from .registry import register_ws_controller, get_all_ws_controllers
from .events import EventController


#
# Register web service controllers
#
register_ws_controller(EventController)


def setup_routes():
    """
    Used to setup RESTFul resources.

    """
    #
    # Ensure all kits are loaded, and their web services are registered
    #
    load_kits()
    for kit_installer_class in get_all_kit_installers():
        kit_installer = kit_installer_class()
        kit_installer.register_web_service_controllers()

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
