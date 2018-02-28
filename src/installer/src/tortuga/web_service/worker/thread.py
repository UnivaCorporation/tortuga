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

from .registry import get_all_ws_worker_actions


logger = getLogger(__name__)


def worker_thread(thread_id, thrdmgr):
    """
    Worker thread for async requests

    """
    with thrdmgr.transaction_lock:
        logger.debug('Starting worker thread: {}'.format(thread_id))

    while True:
        request = thrdmgr.queue.get()

        try:
            logger.debug('Thread_id {} processing item: {}'.format(
                thread_id, request['action']))

            for action_class in get_all_ws_worker_actions():
                if request['action'] == action_class.name:
                    action = action_class()
                    action.process_request(request)

        except Exception:
            with thrdmgr.transaction_lock:
                logger.exception('Error processing worker thread')

        finally:
            thrdmgr.queue.task_done()
