# Copyright 2018 Univa Corporation
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

from logging import getLogger


logger = getLogger(__name__)


WS_WORKER_ACTION_REGISTRY = []


def register_ws_worker_action(worker_action_class):
    """
    Registers a web service controller.

    :param worker_action_class: an subclass of TortugaController

    """
    if worker_action_class in WS_WORKER_ACTION_REGISTRY:
        return
    WS_WORKER_ACTION_REGISTRY.append(worker_action_class)
    logger.info('Web service worker registered: {}'.format(
        worker_action_class.__name__))


def get_all_ws_worker_actions():
    """
    Gets a list of all web service controllers

    :return: a list of web service controller instances

    """
    return [wc for wc in WS_WORKER_ACTION_REGISTRY]
