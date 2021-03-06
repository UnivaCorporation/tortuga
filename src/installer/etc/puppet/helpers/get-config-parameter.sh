#!/bin/bash

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


. /opt/tortuga/etc/tortuga.sh

conffile="$1"
section="$2"
option="$3"

python <<ENDL
import sys
import ConfigParser
from tortuga.kit.actions.actionsBase import ActionsBase

class MyConfigFileReader(ActionsBase):
	def getConfigFile(self):
		return '$conffile'

c = MyConfigFileReader()

cfgParser = c.getConfig()

try:
	print cfgParser.get('$section', '$option')
except ConfigParser.NoOptionError:
	sys.exit(1)
ENDL
