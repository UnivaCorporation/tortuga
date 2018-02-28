from .action import WorkerAction
from tortuga.addhost.deleteHostRequest import process_delete_host_request


class DeleteHostWorkerAction(WorkerAction):
    name = 'DELETE'

    def process_request(self, request):
        process_delete_host_request(request['data'])
