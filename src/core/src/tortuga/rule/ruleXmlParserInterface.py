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

from tortuga.exceptions.abstractMethod import AbstractMethod


class RuleXmlParserInterface(object):
    """
    Rule XML parser interface.
    """

    def parse(self, ruleXmlFile): \
            # pylint: disable=no-self-use,unused-argument
        """
        Parse rule file and return rule object.

            Returns:
                rule
            Throws:
                InvalidXml
                TortugaException
        """
        raise AbstractMethod(
            'parse() has to be implemented in the concrete API class.')

    def parseString(self, ruleXmlString): \
            # pylint: disable=no-self-use,unused-argument
        """
        Parse rule string and return rule object.

            Returns:
                rule
            Throws:
                InvalidXml
                TortugaException
        """
        raise AbstractMethod(
            'parseString() has to be implemented in the concrete API'
            ' class.')
