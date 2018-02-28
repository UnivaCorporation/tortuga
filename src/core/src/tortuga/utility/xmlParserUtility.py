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

from tortuga.exceptions.invalidXml import InvalidXml


def getRequiredElementList(node, tag):
    elements = node.getElementsByTagName(tag)
    if not elements:
        raise InvalidXml('XML missing required element: %s' % (tag))
    return elements


def getRequiredElement(node, tag):
    elements = getRequiredElementList(node, tag)
    # Try to find direct child first.
    for n in elements:
        if n.parentNode.nodeName == node.nodeName:
            return n
    return elements[0]


def getOptionalElementList(node, tag):
    elements = node.getElementsByTagName(tag)
    return elements


def getOptionalElement(node, tag):
    elements = node.getElementsByTagName(tag)
    if not elements:
        return None
    # Try to find direct child first.
    for n in elements:
        if n.parentNode.nodeName == node.nodeName:
            return n
    return elements[0]


def getRequiredTextElement(node, tag):
    return getRequiredElement(node, tag).firstChild.nodeValue


def getOptionalTextElement(node, tag):
    try:
        return getRequiredElement(node, tag).firstChild.nodeValue
    except Exception:
        return ''


def getRequiredAttribute(node, attrName):
    if node.hasAttribute(attrName):
        return node.getAttribute(attrName)
    raise InvalidXml('XML missing required attribute: %s' % (attrName))


def getOptionalAttribute(node, attrName):
    try:
        return getRequiredAttribute(node, attrName)
    except Exception:
        return ''
