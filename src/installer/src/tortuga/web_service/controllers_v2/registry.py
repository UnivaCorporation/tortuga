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

import logging
from typing import List, Type

from tortuga.logging import WEBSERVICE_NAMESPACE
from .base import Controller

logger = logging.getLogger(WEBSERVICE_NAMESPACE)


WS_CONTROLLER_REGISTRY: List[Type[Controller]] = []


def register_ws_controller(controller_class: Type[Controller]):
    """
    Registers a web service controller.

    :param Type[Controller] controller_class: an subclass of TortugaController

    """
    if controller_class in WS_CONTROLLER_REGISTRY:
        return
    WS_CONTROLLER_REGISTRY.append(controller_class)
    logger.info('Web service v2 controller registered: {}'.format(
        controller_class.__name__))


def get_all_ws_controllers() -> List[Type[Controller]]:
    """
    Gets a list of all web service controllers

    :return List[Type[Controller]]: a list of web service controller instances

    """
    return [wc for wc in WS_CONTROLLER_REGISTRY]
