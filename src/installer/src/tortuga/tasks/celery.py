from celery import Celery


app = Celery(
    'tortuga.tasks.queue',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    include=[
        'tortuga.resourceAdapter.tasks',
    ]
)


if __name__ == '__main__':
    app.start()
