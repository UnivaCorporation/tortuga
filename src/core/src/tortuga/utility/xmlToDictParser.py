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

from xml.dom import minidom
from xml.dom import Node
from xml.sax.saxutils import unescape

import types


# Wrapper class for dicts to help with converison to TortugaObjects
class ParseObject(object):
    def has_key(self, key):
        return key in self.__dict__

    def get(self, key, def_val=None):
        return self.__dict__.get(key, def_val)

    def set(self, key, value):
        self.__dict__[key] = value

    def pop(self, key):
        return self.__dict__.pop(key)


def unescapeAll(value):
    return unescape(value, {"&apos;": "'", "&quot;": '"'})


def parseToDict(xmlString, rootTagName, skipElements=None):
    """ Parse xml string into python dict. """
    xmlDoc = minidom.parseString(xmlString)
    rootElement = xmlDoc.getElementsByTagName(rootTagName)
    result_dict = {}
    if rootElement and rootElement[0]:
        rootNode = rootElement[0]
        result_dict = getNodeValue(rootNode, skipElements or [])
    return result_dict


def getNodeValue(node, skipElements=None):
    dict_ = {}

    for attr in list(node.attributes.keys()):
        if skipElements and attr in skipElements:
            continue

        dict_[attr] = unescapeAll(
            node.attributes.get(attr).firstChild.nodeValue)

    for cNode in node.childNodes:
        if cNode.nodeType == Node.TEXT_NODE:
            value = cNode.nodeValue.lstrip().rstrip()
            if value != '':
                return unescapeAll(cNode.nodeValue)
        elif cNode.nodeType == Node.COMMENT_NODE:
            continue
        else:
            tagName = cNode.tagName
            listTagName = '%ss' % tagName

            if listTagName in dict_:
                dict_.get(listTagName).append(
                    getNodeValue(cNode, skipElements or []))
            elif tagName in dict_:
                element = dict_.get(tagName)

                if not isinstance(element, list):
                    dict_[listTagName] = []
                    dict_[listTagName].append(dict_.pop(tagName))

                dict_[listTagName].append(getNodeValue(cNode,
                                                       skipElements or []))
            else:
                if skipElements and tagName in skipElements:
                    continue

                dict_[tagName] = getNodeValue(cNode, skipElements or [])

    return dict_
