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

from typing import List

from marshmallow import fields

from .base import BaseEventSchema, BaseEvent


class TaskFailedSchema(BaseEventSchema):
    """
    Schema for the TaskFailed events.

    """
    task_id = fields.String()
    task_name = fields.String()
    task_error = fields.String()
    task_args = fields.List(fields.String())
    task_kwargs = fields.Dict()
    task_trace = fields.String()


class TaskFailed(BaseEvent):
    """
    Event that fires when a celery task fails.

    """
    name = 'task-failed'
    schema_class = TaskFailedSchema

    def __init__(self, **kwargs):
        """
        Initializer.

        :param str node:     the current state of the node affected
        :param dict request: the previous state
        :param kwargs:

        """
        super().__init__(**kwargs)
        self.task_id: str = kwargs.get('task_id', None)
        self.task_name: str = kwargs.get('task_name', None)
        self.task_error: str = kwargs.get('task_error', None)
        self.task_args: list = kwargs.get('task_args', [])
        self.task_kwargs: dict = kwargs.get('task_kwargs', {})
        self.task_trace: str = kwargs.get('task_trace', None)
