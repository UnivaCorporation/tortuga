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

from sqlalchemy import Sequence
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.orm import mapper

from .mapper import TableMapper
from ..globalParameters import GlobalParameters


class GlobalParamsTableMapper(TableMapper):
    def map(self, db_manager):
        backend_opts = db_manager.get_backend_opts()

        global_params_table = Table(
            'GlobalParameters',
            db_manager.metadata,
            Column('id', Integer, Sequence('globalparameters_seq_id'),
                   primary_key=True),
            Column('name', String(255), nullable=False, unique=True),
            Column('value', String(255)),
            Column('description', String(255)),
            **backend_opts
        )

        mapper(GlobalParameters, global_params_table)
