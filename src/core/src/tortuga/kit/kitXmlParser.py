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

import os.path
from xml.dom import minidom
import logging
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.objects.kit import Kit
from tortuga.objects.component import Component
from tortuga.objects.osInfo import OsInfo
from tortuga.objects.osFamilyInfo import OsFamilyInfo
from tortuga.objects.packageFile import PackageFile
from tortuga.objects.eula import Eula


def _process_component_os(osNode, component):
    bIsOsFamily = not osNode.hasAttribute('name')

    osName = osNode.getAttribute('name') \
        if not bIsOsFamily else osNode.getAttribute('family')

    osVersion = osNode.getAttribute('version') \
        if osNode.hasAttribute('version') else None

    osArch = osNode.getAttribute('arch') \
        if osNode.hasAttribute('arch') else None

    osFamilyInfo = None
    osInfo = None

    if bIsOsFamily:
        osFamilyInfo = OsFamilyInfo(osName, osVersion, osArch)
        component.addOsFamilyInfo(osFamilyInfo)
    else:
        osInfo = OsInfo(osName, osVersion, osArch)
        component.addOsInfo(osInfo)

    for pNode in osNode.getElementsByTagName('package'):
        component.addPackage(PackageFile(pNode.getAttribute('path')))

    return osInfo or osFamilyInfo


def parse(kitXmlFile):
    """Parse kit information for a given os and return kit object."""

    logger = logging.getLogger('tortuga.kit.parse')
    logger.addHandler(logging.NullHandler())

    try:
        logger.debug('parse(): parsing [%s]' % (kitXmlFile))

        xmlDoc = minidom.parse(kitXmlFile)

        rootNode = xmlDoc.getElementsByTagName('kit')[0]

        kit = Kit(name=rootNode.getAttribute('name'),
                  version=rootNode.getAttribute('version'),
                  iteration=rootNode.getAttribute('iteration'))

        documentationNode = rootNode.getElementsByTagName('documentation')[0]

        kit.setDocumentation(documentationNode.getAttribute('path'))

        eulaNodes = rootNode.getElementsByTagName('eula')

        if len(eulaNodes):
            try:
                with open(os.path.join(os.path.dirname(kitXmlFile),
                                       eulaNodes[0].getAttribute('path')),
                          'r') as f:
                    textContents = f.read()

                kit.setEula(
                    Eula(eulaNodes[0].getAttribute('key'), textContents))
            except Exception:
                logger.exception('Exception raised parsing EULA from kit')

                logger.debug('Unable to load EULA file contents')

        kit.setIntegrationModulePath(
            rootNode.getElementsByTagName('integration-module')[0].
            getAttribute('path'))

        kit.setDescription(
            rootNode.getElementsByTagName('description')[0].firstChild.
            nodeValue)

        for cNode in xmlDoc.getElementsByTagName('component'):
            component = Component(name=cNode.getAttribute('name'),
                                  version=cNode.getAttribute('version'))

            logger.debug(
                'parse(): Found component [%s]' % (component.getName()))

            # Kit description
            nodeList = cNode.getElementsByTagName('description')
            if nodeList:
                component.setDescription(nodeList[0].firstChild.nodeValue)

            # process os elements
            for osNode in cNode.getElementsByTagName('os'):
                result = _process_component_os(osNode, component)

                logger.debug(
                    'parse(): Adding component [%s] for [%s]' % (
                        component, result))

            kit.addComponent(component)

        return kit
    except TortugaException:
        raise
    except Exception as ex:
        logger.exception('Exception raised while parsing [%s]' % (kitXmlFile))

        raise TortugaException(exception=ex)
