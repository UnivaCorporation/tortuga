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
from xml.dom.minidom import parse
from tortuga.exceptions.tortugaException import TortugaException


class NoDomElement(TortugaException):
    """Missing XML element exception"""


class NoDomAttribute(TortugaException):
    """Missing XML attribute exception """


class DOM(object):
    def __init__(self, xmlpath):
        self._logger = logging.getLogger('tortuga.kit.actions.DOM')
        self._logger.addHandler(logging.NullHandler())

        try:
            self.dom = parse(xmlpath)
        except Exception as msg:
            self._logger.error("Can't parse [%s]; %s" % (xmlpath, msg))
            raise

        self.xmlpath = xmlpath

    def get_element_list(self, tag, root=None):
        if not root:
            root = self.dom

        elements = root.getElementsByTagName(tag)
        if not elements:
            raise NoDomElement(
                "Missing element [%s] in [%s]" % (tag, self.xmlpath))

        return elements

    def get_attribute(self, tag, element):
        try:
            return element.attributes[tag].value
        except Exception:
            raise NoDomAttribute(
                "Missing attribute [%s] in element [%s] in [%s]" % (
                    tag, element.tagName, self.xmlpath))

    def get_element(self, tag, root=None):
        return self.get_element_list(tag, root)[0]

    def get_text_element(self, tag, root=None):
        return self.get_element(tag, root).firstChild.data
