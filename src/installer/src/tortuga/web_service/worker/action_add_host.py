from .action import WorkerAction
from tortuga.addhost.addHostRequest import process_addhost_request


class AddHostWorkerAction(WorkerAction):
    name = 'ADD'

    def process_request(self, request):
        process_addhost_request(request['data']['addHostSession'])
