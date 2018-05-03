#!/usr/bin/env python

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

# pylint: disable=no-member

import configparser
import pprint
import sys
import urllib.parse

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.config.configManager import ConfigManager
from tortuga.exceptions.invalidArgument import InvalidArgument
from tortuga.kit import kitApiFactory


class TortugaProxyConfig(TortugaCli):
    def __init__(self):
        super(TortugaProxyConfig, self).__init__(validArgCount=4)

        self._cm = ConfigManager()
        self._kitApi = kitApiFactory.getKitApi()

    def parseArgs(self, usage=None):
        # TODO: add stuff here
        self.addOption('-f', '--force', action='store_true', default=False,
                       dest='bForce',
                       help='Override built-in sanity checks')

        self.addOption('-n', '--dry-run', action='store_true',
                       dest='bDryRun', default=False,
                       help='Do not write anything to disk')

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs()

        if self.getNArgs() < 1:
            self.usage()

            return

        action = self.getArgs()[0]

        if action == 'list':
            self._listProxies()
        elif action == 'add':
            if self.getNArgs() != 3:
                self.usage()
                return

            self._addProxy()
        elif action == 'delete':
            self._deleteProxy()
        else:
            raise InvalidArgument('Unknown directive [%s]' % (action))

    def _getProxyCfg(self): \
            # pylint: disable=no-self-use
        cfg = configparser.ConfigParser()

        cfg.read('/opt/tortuga/config/base/apache-component.conf')

        return cfg

    def __get_proxy_set(self, cfg): \
            # pylint: disable=no-self-use
        return set(cfg.get('proxy', 'proxy_list').split(' ')) \
            if cfg.has_option('proxy', 'proxy_list') else set()

    def _getProxyMap(self, cfg):
        proxyMap = {}

        if not cfg.has_section('proxy'):
            return proxyMap

        proxy_option_list = self.__get_proxy_set(cfg)

        for opt in proxy_option_list:
            if not cfg.has_option('proxy', opt):
                continue

            proxyMap[opt] = cfg.get('proxy', opt)

        return proxyMap

    def _writeProxyMap(self, cfg, proxyMap):
        if not cfg.has_section('proxy'):
            cfg.add_section('proxy')

        # Determine differences between what exists on disk and what has
        # just been removed.
        for deleted_option in self.__get_proxy_set(cfg) - set(proxyMap.keys()):
            if not cfg.has_option('proxy', deleted_option):
                continue

            cfg.remove_option('proxy', deleted_option)

        cfg.set('proxy', 'proxy_list', ' '.join(list(proxyMap.keys())))

        for key, value in proxyMap.items():
            cfg.set('proxy', key, value)

        proxyDict = dict(cfg.items('proxy'))

        if self.getArgs().bDryRun:
            print('[dryrun] %s' % (pprint.pformat(proxyDict)))
            return

        with open('/opt/tortuga/config/base/apache-component.conf', 'w') as fp:
            cfg.write(fp)

    def _addProxy(self):
        proxy_from = self.getArgs()[1]
        proxy_to = self.getArgs()[2]

        cfg = self._getProxyCfg()

        proxyMap = self._getProxyMap(cfg)

        if proxy_from in proxyMap:
            if proxy_to == proxyMap[proxy_from]:
                print('Proxy already mapped')

                sys.exit(1)

            if not self.getArgs().bForce:
                print('URI [%s] is already proxied to [%s]' % (
                    proxy_from, proxyMap[proxy_from]))

                sys.exit(1)

        proxyMap[proxy_from] = proxy_to

        self._writeProxyMap(cfg, proxyMap)

    def __find_kit_by_name_and_version(self, os_name, os_version):
        """
        Iterate over list of all installed kits looking for a name and
        version match only.

        Returns Kit object, otherwise None.
        """

        kit = None

        for kit in self._kitApi.getKitList():
            if kit.getName() == os_name and \
               kit.getVersion() == os_version:
                break
        else:
            return None

        return kit

    def __get_existing_kit_by_url(self, proxy_uri):
        """
        Given a proxy URI, determine if the path matches that of an
        installed kit. Returns Kit object or None.
        """

        uri_parts = proxy_uri.split('/')

        if len(uri_parts) != 5:
            # Short-circuit any check if the URI is longer/shorter than
            # a properly formatted Tortuga kit URL.
            return None

        # Check if this URI is formatted like valid OS kit URL

        os_name = uri_parts[2]
        os_version = uri_parts[3]
        os_arch = uri_parts[4]

        fake_url = self._cm.getYumRootUrl('INSTALLER') + '/%s/%s/%s' % (
            os_name, os_version, os_arch)

        o = urllib.parse.urlparse(fake_url)

        if o.path != proxy_uri:
            # The paths don't start with the requisite Tortuga path
            return None

        version = os_version.split('-')

        # Check if supplied 'version' element of the path matches the
        # Tortuga convention.

        if len(version) == 1:
            # Possibly an OS kit
            # bOsKit = True if os_arch == 'x86_64' else None
            pass
        elif len(version) == 2:
            # Possibly a non-OS kit. Non-OS kits must have the 'arch'
            # set to 'noarch'
            # bOsKit = False if os_arch == 'noarch' else None
            pass
        else:
            # version element doesn't match Tortuga format
            return None

        return self.__find_kit_by_name_and_version(os_name, os_version)

    def _deleteProxy(self):
        proxy_path = self.getArgs()[1]

        cfg = self._getProxyCfg()

        proxyMap = self._getProxyMap(cfg)

        if proxy_path in proxyMap:
            existingKit = self.__get_existing_kit_by_url(proxy_path)

            if existingKit and not self.getArgs().bForce:
                print('WARNING: an installed %s [%s] matches this URL.'
                      ' Use \'--force\' to override this sanity check.' % (
                          'OS kit' if existingKit.getIsOs() else 'kit',
                          existingKit))

                sys.exit(1)

        if proxy_path not in proxyMap:
            print('Error: proxy path [%s] not found' % (proxy_path))

            sys.exit(1)

        del proxyMap[proxy_path]

        self._writeProxyMap(cfg, proxyMap)

    def _listProxies(self):
        cfg = self._getProxyCfg()

        for key, value in self._getProxyMap(cfg).items():
            print('%s -> %s' % (key, value))


def main():
    TortugaProxyConfig().run()
