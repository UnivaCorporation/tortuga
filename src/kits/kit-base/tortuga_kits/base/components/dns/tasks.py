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

from celery.schedules import crontab

from tortuga.tasks.celery import app
from .component import DnsmasqDnsProvider

logger = logging.getLogger(__name__)


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    #
    # Reload the dnsmasq service every 5 minutes, if required
    #
    sender.add_periodic_task(
        crontab(minute="*/5"),
        reload_dnsmasq.s(),
    )


@app.task()
def reload_dnsmasq():
    DnsmasqDnsProvider.reload()

