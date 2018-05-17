from tortuga.tasks import app
from tortuga.addhost.addHostRequest import process_addhost_request
from tortuga.addhost.deleteHostRequest import process_delete_host_request


@app.task()
def add_nodes(session_id):
    process_addhost_request(session_id)


@app.task()
def delete_nodes(transaction_id, nodespec):
    process_delete_host_request(transaction_id, nodespec)
