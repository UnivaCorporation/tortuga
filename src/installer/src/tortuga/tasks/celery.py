from typing import List

from celery import Celery

from tortuga.kit.loader import load_kits
from tortuga.kit.registry import get_all_kit_installers


load_kits()
kits_task_modules: List[str] = []
for kit_installer in get_all_kit_installers():
    kits_task_modules += kit_installer.task_modules


app = Celery(
    'tortuga.tasks.queue',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    include=[
        'tortuga.resourceAdapter.tasks',
    ] + kits_task_modules
)


if __name__ == '__main__':
    app.start()
