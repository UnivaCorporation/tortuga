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

# pylint: disable=no-member,no-self-use

import base64
import json
import xml.etree.cElementTree as ET
from typing import Iterable, Optional


def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


class TortugaObject(dict): \
        # pylint: disable=too-many-public-methods

    """
    Base tortuga object class.
    """

    def __init__(self, _dict=None, attributeList=None, rootTag=None,
                 encodedKeyTypeDict=None):
        """
        dict gets the parameters passed to the object's constructor.
        attributeList gets the names of those properties that should be
        rendered as XML attributes, instead of XML elements.
        encodedKeyTypeDict is a dictionary of types of objects that are
        encoded using 'encode' method.
        """

        dict.__init__(self, _dict or {})

        self._attributeList = attributeList or []
        self._encodedKeyTypeDict = encodedKeyTypeDict or {}
        self._rootTag = rootTag

        if not rootTag:
            self._rootTag = self.__class__.__name__.lower()

    def setAttributeList(self, attributeList=None):
        """ Set attribute list. """
        self._attributeList = attributeList or []

    def getAttributeList(self):
        """ Get attribute list. """
        return self._attributeList

    def setEncodedKeyTypeDict(self, encodedKeyTypeDict=None):
        """ Set encoded key list. """
        self._encodedKeyTypeDict = encodedKeyTypeDict or {}

    def getEncodedKeyTypeDict(self):
        """ Get encoded key list. """
        return self._encodedKeyTypeDict

    def setRootTag(self, rootTag):
        """ Set root tag. """
        self._rootTag = rootTag

    def getRootTag(self):
        """ Get root tag. """
        return self._rootTag

    def set(self, key, value):
        """ Set value for the given key. Ignore 'None' values. """
        if value is not None:
            self[key] = value

    @classmethod
    def getFromXml(cls, xmlString, skipElements=None):
        from tortuga.utility import xmlToDictParser

        objectDict = xmlToDictParser.\
            parseToDict(xmlString, cls.ROOT_TAG, skipElements or [])

        if objectDict is not None:
            # Got our target dict
            return cls.getFromDict(objectDict)
        return None

    @staticmethod
    def getKeys():
        return []

    @classmethod
    def getFromDict(cls, _dict, ignore: Optional[Iterable[str]] = None):
        inst = cls()

        for key in cls.getKeys():
            if ignore and key in ignore:
                continue

            if key not in _dict:
                inst[key] = None
                continue

            inst[key] = _dict[key]

        return inst

    @classmethod
    def getFromDbDict(cls, _dict, ignore: Optional[Iterable[str]] = None):
        return cls.getFromDict(_dict, ignore=ignore)

    @classmethod
    def getListFromDict(cls, dict_, ignore: Optional[Iterable[str]] = None):
        dictList = []

        tag = cls.ROOT_TAG

        if '%ss' % (tag) in dict_:
            dictList = dict_['%ss' % (tag)]
        else:
            # Single element
            if tag in dict_:
                dictList = [dict_[tag]]

        return TortugaObjectList([cls.getFromDict(d) for d in dictList])

    @classmethod
    def getListFromDbDict(cls, _dict, ignore: Optional[Iterable[str]] = None):
        dictList = []

        tag = cls.ROOT_TAG

        if '%ss' % (tag) in _dict:
            dictList = _dict['%ss' % (tag)]
        else:
            # Single element
            if tag in _dict:
                dictList = [_dict[tag]]

        return TortugaObjectList(
            [cls.getFromDbDict(d.__dict__, ignore=ignore) for d in dictList])

    def getPrettyXmlString(self, root): \
            # pylint: disable=unused-argument
        rootElement = self.getXmlDom().getroot()

        indent(rootElement)

        return ET.tostring(rootElement)

    def getXmlRep(self):
        return self.getPrettyXmlString(self.getXmlDom().getroot()).decode()

    def getXmlDom(self, parent=None):
        """
        Returns:
            xml.etree.ElementTree.ElementTree
        """

        parentElement = ET.Element(self._rootTag)

        if parent is None:
            domRoot = ET.ElementTree(parentElement)
        else:
            parent.append(parentElement)
            domRoot = None

        for attr in [attr for attr in self._attributeList
                     if self.get(attr) is not None]:
            parentElement.set(attr, str(self[attr]))

        for key, value in self.items():
            if self._attributeList.count(key):
                continue

            if isinstance(value, TortugaObject):
                value.getXmlDom(parentElement)
            elif isinstance(value, TortugaObjectList):
                for item in value:
                    item.getXmlDom(parentElement)
            elif isinstance(value, dict):
                root_element = ET.SubElement(parentElement, key)
                for key_, value_ in value.items():
                    element = ET.SubElement(root_element, key[:-1])
                    element.set('name', key_)
                    element.set('value', value_)
            else:
                if self.get(key) is not None:
                    element = ET.SubElement(parentElement, key)
                    element.text = str(value)

        return domRoot

    def getCleanDict(self):
        dataDict = {}

        for key, value in self.items():
            if isinstance(value, TortugaObject) or \
               isinstance(value, TortugaObjectList):
                dataDict[key] = value.getCleanDict()
                continue

            dataDict[key] = self.get(key)

        return dataDict

    def getJsonRep(self):
        return json.dumps(self.getCleanDict())

    def encode(self):
        """ Encode values for listed keys. """
        for key, value in self.items():
            if isinstance(value, TortugaObject):
                value.encode()
            elif isinstance(value, TortugaObjectList):
                value.encode()
            else:
                if key in self._encodedKeyTypeDict:
                    self[key] = base64.\
                        b64encode(base64.encodestring(str(value)))

    def decode(self):
        """ Decode values for listed keys. """
        for key, value in self.items():
            if isinstance(value, TortugaObject):
                value.decode()
            elif isinstance(value, TortugaObjectList):
                value.decode()
            else:
                if key in self._encodedKeyTypeDict:
                    if not value:
                        continue

                    value = base64.\
                        decodestring(base64.b64decode(str(value)))

                    keyType = self._encodedKeyTypeDict.get(key)

                    try:
                        exec('self[key] = %s(%s)' % (keyType, value))
                    except Exception:
                        # Did not work, leave as is.
                        self[key] = value


class TortugaObjectList(list):
    """
    Base tortuga object list class.
    """

    def getXmlRep(self):
        xmlDom = self.getXmlDom()

        result = ''

        for element in xmlDom.getroot().getchildren():
            result += self.getPrettyXmlElementString(element)

        return result

    def getXmlDom(self, parent=None):
        """
        Do not use this method for dumping a mixed list of Tortuga
        objects and non-Tortuga objects. In fact, don't do that ever
        anyway. The TortugaObjectList construct does not support it.
        """

        parentElement = parent

        for obj in self:
            if parentElement is None:
                # pylint: disable=protected-access
                parentElement = ET.Element(obj._rootTag)

            obj.getXmlDom(parentElement)

        if parent is None:
            return ET.ElementTree(parentElement)

        return parentElement

    def getPrettyXmlString(self):
        return self.getPrettyXmlElementString(self.getXmlDom().getroot())

    def getPrettyXmlElementString(self, element):
        indent(element)
        return ET.tostring(element)

    def getCleanDict(self):
        dataDict = []

        for obj in self:
            if isinstance(obj, TortugaObject):
                dataDict.append(obj.getCleanDict())
                continue

            dataDict.append(obj)

        return dataDict

    def encode(self):
        for obj in self:
            if isinstance(obj, TortugaObject):
                obj.encode()

    def decode(self):
        for obj in self:
            if isinstance(obj, TortugaObject):
                obj.decode()
