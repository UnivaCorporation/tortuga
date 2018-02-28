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

from tortuga.addhost.addHostRequest import process_addhost_request
from tortuga.addhost.deleteHostRequest import process_delete_host_request
from tortuga.uge_mgmt import wsapirequest


def worker_thread(thread_id, thrdmgr):
    """Worker thread for async requests"""

    with thrdmgr.transaction_lock:
        thrdmgr.getLogger().debug(
            'worker_thread(): starting worker thread %d' % (thread_id))

    while True:
        request = thrdmgr.queue.get()

        try:
            thrdmgr.getLogger().debug(
                'worker_thread(): thread_id: %d: processing'
                ' item %s' % (thread_id, request['action']))

            if request['action'] == 'ADD':
                process_addhost_request(request['data']['addHostSession'])
            elif request['action'] == 'DELETE':
                process_delete_host_request(request['data'])
            elif request['action'] == 'UGE-CLUSTER-ADD':
                wsapirequest.process_uge_cluster_add(request['data'])
            elif request['action'] == 'UGE-CLUSTER-UPDATE':
                wsapirequest.process_uge_cluster_update(request['data'])
            elif request['action'] == 'UGE-CLUSTER-DELETE':
                wsapirequest.process_uge_cluster_delete(request['data'])
        except Exception:
            with thrdmgr.transaction_lock:
                thrdmgr.getLogger().exception('Error processing worker thread')
        finally:
            thrdmgr.queue.task_done()
