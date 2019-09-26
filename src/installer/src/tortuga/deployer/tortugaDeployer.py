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

# pylint: disable=no-name-in-module,no-member

import configparser
import gettext
import glob
import itertools
import os
import pwd
import random
import shutil
import string
import subprocess
import sys
import time
from typing import Any, Tuple

import yaml
from six import print_

from sqlalchemy.orm.session import Session
from tortuga.admin.api import AdminApi
from tortuga.config.configManager import ConfigManager, getfqdn
from tortuga.deployer import dbUtility
from tortuga.exceptions.commandFailed import CommandFailed
from tortuga.exceptions.eulaAcceptanceRequired import EulaAcceptanceRequired
from tortuga.exceptions.invalidArgument import InvalidArgument
from tortuga.exceptions.invalidMachineConfiguration import \
    InvalidMachineConfiguration
from tortuga.exceptions.kitNotFound import KitNotFound
from tortuga.exceptions.softwareAlreadyDeployed import SoftwareAlreadyDeployed
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.helper.osHelper import getOsInfo
from tortuga.kit.kitApi import KitApi
from tortuga.kit.loader import load_kits
from tortuga.kit.utils import get_metadata_from_archive
from tortuga.node.nodeApi import NodeApi
from tortuga.os_utility import osUtility, tortugaSubprocess
from tortuga.os_utility.osUtility import getOsObjectFactory
from tortuga.softwareprofile.softwareProfileApi import SoftwareProfileApi


class TortugaDeployer: \
        # pylint: disable=too-many-public-methods
    def __init__(self, logger, cmdline_options=None):
        self._cm = ConfigManager()

        self._logger = logger

        self._osObjectFactory = osUtility.getOsObjectFactory()

        self._settings = self.__load_settings(cmdline_options)

        self._settings['installer_software_profile'] = 'Installer'
        self._settings['installer_hardware_profile'] = 'Installer'

        self._settings['eulaAccepted'] = False

        self._settings['fqdn'] = getfqdn()

        self._settings['osInfo'] = getOsInfo()

        self._forceCleaning = False
        self._depotCreated = False

        fsManager = self._osObjectFactory.getOsFileSystemManager()

        self._lockFilePath = os.path.join(
            fsManager.getOsLockFilePath(), 'tortuga-setup')

        langdomain = 'tortuga-config'

        localedir = os.path.join(self._cm.getRoot(), 'share', 'locale')

        if not os.path.exists(localedir):
            # Try the system path
            localedir = '/usr/share/locale'

        gettext.bindtextdomain(langdomain, localedir)
        gettext.textdomain(langdomain)
        self.gettext = gettext.gettext
        self._ = self.gettext

        self._logger.info('Detected OS: [%s]', self._settings['osInfo'])

    def __load_settings(self, cmdline_options):
        settings = dict(list(cmdline_options.items()))

        default_cfgfile = os.path.join(
            self._cm.getKitConfigBase(), 'tortuga.ini')

        if 'inifile' in cmdline_options and \
                cmdline_options['inifile'] != default_cfgfile:
            # Copy configuration specified on command-line to
            # $TORTUGA_ROOT/config/tortuga.ini

            self._logger.info(
                'Using configuration file [%s]' % (settings['inifile']))

            self._logger.info(
                'Copying configuration to [%s]' % (default_cfgfile))

            if os.path.exists(default_cfgfile):
                # Back up existing 'tortuga.ini'
                shutil.move(default_cfgfile, default_cfgfile + '.orig')

            shutil.copyfile(cmdline_options['inifile'], default_cfgfile)

        settings['inifile'] = default_cfgfile

        cfg = configparser.ConfigParser()
        cfg.read(settings['inifile'])

        settings['timezone'] = ''
        settings['utc'] = False
        settings['keyboard'] = 'us'
        settings['language'] = 'en_US.UTF-8'

        # Get database setting
        value = cfg.get('database', 'engine') \
            if cfg.has_section('database') and \
            cfg.has_option('database', 'engine') else None

        if value and value not in ('mysql', 'sqlite'):
            raise InvalidArgument(
                'Unsupported database engine [%s]' % (value))

        settings['database'] = {
            'engine': value if value else 'mysql'
        }

        # Get depot directory
        if cfg.has_section('installer') and \
                cfg.has_option('installer', 'depotpath'):
            settings['depotpath'] = cfg.get('installer', 'depotpath')

            # For consistency's sake...
            self._cm.setDepotDir(settings['depotpath'])
        else:
            settings['depotpath'] = self._cm.getDepotDir()

        # Internal web port
        settings['intWebPort'] = cfg.getint('installer', 'intWebPort') \
            if cfg.has_section('installer') and \
            cfg.has_option('installer', 'intWebPort') else \
            self._cm.getIntWebPort()

        self._cm.setIntWebPort(settings['intWebPort'])

        # Admin port
        settings['adminPort'] = cfg.getint('installer', 'adminPort') \
            if cfg.has_section('installer') and \
            cfg.has_option('installer', 'adminPort') else \
            self._cm.getAdminPort()

        self._cm.setAdminPort(settings['adminPort'])

        # IntWebServicePort
        settings['intWebServicePort'] = cfg.getint(
            'installer', 'intWebServicePort') \
            if cfg.has_section('installer') and \
            cfg.has_option('installer', 'intWebServicePort') else \
            self._cm.getIntWebServicePort()

        self._cm.setIntWebServicePort(settings['intWebServicePort'])

        return settings

    def _get_setting(self, name, section=None):
        if section and section in self._settings:
            return self._settings[section][name] \
                if name in self._settings[section] else None

        return self._settings[name] if name in self._settings else None

    def eout(self, message, *args):
        """
        Output messages to STDERR with Internationalization.
        Additional arguments will be used to substitute variables in the
        message output
        """
        if args:
            mesg = self.gettext(message) % args
        else:
            mesg = self.gettext(message)
        sys.stderr.write(mesg)

    def out(self, message, *args):
        """
        Output messages to STDOUT with Internationalization.
        Additional arguments will be used to substitute variables in the
        message output
        """
        if args:
            mesg = self.gettext(message) % args
        else:
            mesg = self.gettext(message)
        sys.stdout.write(mesg)

    def prompt(self, default_value,
               auto_answer_default_value, text_list, question,
               tag=None, section=None, isPassword=False):
        """Generic user prompting routine"""

        resp_value = None

        bDefaults = self._settings['defaults']

        if tag:
            resp_value = self._get_setting(tag, section=section)
            if not resp_value and bDefaults:
                # Use the default value
                default_value = auto_answer_default_value
        elif bDefaults:
            default_value = auto_answer_default_value

        if text_list:
            self.out('\n')

            for line in text_list:
                self.out(line + '\n')

        if default_value and not isPassword:
            self.out('\n%s [%s]: ' % (question, default_value))
        else:
            self.out('\n%s: ' % (question))

        if bDefaults or resp_value:
            if resp_value:
                value = resp_value
            else:
                value = auto_answer_default_value
            if not isPassword:
                self.out('%s\n' % value)
        else:
            if isPassword:
                import getpass
                value = getpass.getpass('').strip()
            else:
                value = input('').strip()
            if not value:
                value = default_value

        return value

    def checkPreInstallConfiguration(self):     # pylint: disable=no-self-use
        """
        Raises:
            InvalidMachineConfiguration
        """

        # Check for existence of /etc/hosts
        if not os.path.exists('/etc/hosts'):
            raise InvalidMachineConfiguration(
                '/etc/hosts file is missing. Unable to proceed with'
                ' installation')

    def preInstallPrep(self):
        bAcceptEula = self._settings['acceptEula']

        license_file = ' %s/LICENSE' % (self._cm.getEtcDir())

        print()

        if bAcceptEula:
            cmd = 'cat %s\n' % (license_file)
            os.system(cmd)
        else:
            cmd = 'more %s\n' % (license_file)

            print("To install Tortuga you must read and agree to "
                  "the following EULA.")

            print("Press 'Enter' to continue...")

            input('')
            os.system(cmd)
            print()
            while True:
                print('Do you agree? [Yes / No]', end=' ')
                answer = input('').lower()

                if answer not in ['yes', 'no', 'y', 'n']:
                    print('Invalid response. Please respond \'Yes\''
                          ' or \'No\'')

                    continue
                break
            if answer[0] == 'n':
                raise EulaAcceptanceRequired(
                    'You must accept the EULA to install Tortuga')

        self._settings['eulaAccepted'] = \
            'Accepted on: %s local machine time' % (time.ctime())

        # Restore resolv.conf if we have a backup
        if osUtility.haveBackupFile('/etc/resolv.conf'):
            osUtility.restoreFile('/etc/resolv.conf')

    def _runCommandWithSpinner(self, cmd, statusMsg, logFileName):
        self._logger.debug(
            '_runCommandWithSpinner(cmd=[%s], logFileName=[%s])' % (
                cmd, logFileName))

        self.out(statusMsg + '  ')

        # Open the log file in unbuffered mode
        fpOut = open(logFileName, 'ab', 0)

        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, bufsize=1,
                             close_fds=True)

        for i in itertools.cycle(['/', '-', '\\', '|']):
            buf = p.stdout.readline()

            sys.stdout.write('')
            sys.stdout.flush()

            if not buf:
                break

            fpOut.write(buf)

            sys.stdout.write(i)
            sys.stdout.flush()

        sys.stdout.write(' ')
        self.out('done.\n')

        retval = p.wait()

        fpOut.close()

        return retval

    def puppetApply(self):
        '''
        Complete the installer configuration by running against the
        previously installed Puppet master.  Display a spinner while Puppet
        runs.
        '''

        self._logger.info('Running Puppet for post-configuration')

        logFileName = '/tmp/tortuga_setup.log'

        cmd = ('/opt/puppetlabs/bin/puppet agent --color false --onetime'
               ' --no-daemonize --detailed-exitcodes --verbose 2>&1')

        retval = self._runCommandWithSpinner(
            cmd, statusMsg=(
                '\nCompleting installer configuration.'
                ' Please wait...'), logFileName=logFileName)

        if retval not in (0, 2):
            # Puppet can return a non-zero return code, even if it was
            # successful.

            errmsg = 'Puppet post-configuration failed (see log file %s)' % (
                logFileName)

            self._logger.error(errmsg)

            self.out(errmsg + '\n')

            raise Exception(errmsg)

        self._logger.info('Puppet post-configuration completed')

    def startSetup(self):
        # If force was specified clean first and then run...
        bForce = self._settings['force']

        if bForce:
            self._forceCleaning = True

            self.out(
                '--force option specified. Cleaning previous'
                ' installation.\n')

            self.cleanup()

            self._forceCleaning = False

        if os.path.exists(self._lockFilePath):
            raise SoftwareAlreadyDeployed(
                "\ntortuga-setup has already been run.\n\n"
                "Use --force option to force reinstallation.")

        open(self._lockFilePath, 'w').close()

        self.out('Tortuga Setup\n')

    def getClusterConfig(self):
        sysManager = self._osObjectFactory.getOsSysManager()

        self._settings['timezone'], self._settings['utc'] = \
            sysManager.findTimeInfo()

        self._settings['keyboard'] = sysManager.findKeyboard()

        self._settings['language'] = sysManager.findLanguage()

        self.out(_('\nStarting Tortuga setup...\n'))

        # Ports configuration
        if not self._settings['defaults']:
            intWebPort, adminPort, intWebServicePort = self.configurePorts()

            self._cm.setIntWebPort(intWebPort)
            self._cm.setAdminPort(adminPort)
            self._cm.setIntWebServicePort(intWebServicePort)

            self._settings['intWebPort'] = intWebPort
            self._settings['adminPort'] = adminPort
            self._settings['intWebServicePort'] = intWebServicePort

        # Admin username and password
        self._settings['adminUsername'], \
            self._settings['adminPassword'] = self.promptForAdminCredentials()

    def prepDepot(self):
        depotpath = None

        if not self._settings['defaults']:
            self.out(
                _('Tortuga requires a directory for storage of OS'
                  ' distribution media and other files required for'
                  ' node provisioning.\n\n'))

        while not depotpath:
            if self._settings['defaults']:
                response = self._settings['depotpath']
            else:
                try:
                    response = input(
                        'Please enter a depot path (Ctrl-C to interrupt)'
                        ' [%s]: ' % (self._settings['depotpath']))
                except KeyboardInterrupt:
                    raise InvalidArgument(_('Aborted by user.'))

                if not response:
                    response = self._settings['depotpath']

            if not response.startswith('/'):
                errmsg = 'Depot path must be fully-qualified'

                if not self._settings['defaults']:
                    self.out('Error: %s\n' % (errmsg))

                    continue

                raise InvalidArgument(errmsg)

            if response == '/':
                errmsg = 'Depot path cannot be system root directory'

                if not self._settings['defaults']:
                    self.out(_('Error: %s\n' % (errmsg)))

                    continue

                raise InvalidArgument(errmsg)

            if os.path.exists(response):
                if not self._settings['force']:
                    if not self._settings['defaults']:
                        self.out(
                            _('Directory [%s] already exists. Do you wish to'
                              ' remove it [N/y]? ') % (response))

                        remove_response = input('')

                        if not remove_response or \
                                remove_response[0].lower() == 'n':
                            continue_response = input(
                                'Do you wish to continue [N/y]? ')

                            if continue_response and \
                                    continue_response[0].lower() == 'y':
                                continue

                            raise InvalidArgument(_('Aborted by user.'))
                    else:
                        raise InvalidArgument(
                            _('Existing depot directory [%s] will not be'
                              ' removed.') % (response))
                else:
                    self.out(
                        _('\nRemoving existing depot directory [%s]... ') % (
                            response))

                    depotpath = response

                    tortugaSubprocess.executeCommand(
                        'rm -rf %s/*' % (depotpath))

                    self.out(_('done.\n'))
            else:
                depotpath = response

        self._settings['depotpath'] = depotpath

        self._cm.setDepotDir(self._settings['depotpath'])

    def _portPrompt(self, promptStr, defaultValue):
        while True:
            tmpPort = self.prompt(
                defaultValue, defaultValue, None, promptStr)

            try:
                tmpPort = int(tmpPort)

                if tmpPort <= 0 or tmpPort > 65535:
                    raise ValueError('Port must be between 1 and 65535')

                # Success
                break
            except ValueError as ex:
                self.out('Error: ' + str(ex) + '\n')

        return tmpPort

    def configurePorts(self):
        reconfigurePorts = self.prompt(
            'N', 'N', [
                'The following ports will be used by Tortuga:'
                '',
                '    +-----------------------------+-------+',
                '    | Description                 | Port  |',
                '    +-----------------------------+-------+',
                '    | Internal webserver          | %5d |' % (
                    self._settings['intWebPort']),
                '    | SSL webservice daemon       | %5d |' % (
                    self._settings['adminPort']),
                '    | Local webservice daemon     | %5d |' % (
                    self._settings['intWebServicePort']),
                '    +-----------------------------+-------+'
            ], 'Do you wish to change the default configuration [N/y]?')

        if not reconfigurePorts or reconfigurePorts[0].lower() == 'n':
            return self._settings['intWebPort'], \
                self._settings['adminPort'], \
                self._settings['intWebServicePort']

        # Internal web server port
        intWebPort = self._portPrompt(
            'Enter port for internal webserver',
            self._settings['intWebPort'])

        # SSL webservice daemon port
        adminPort = self._portPrompt(
            'Enter port for SSL webservice daemon',
            self._settings['adminPort'])

        # Local webservice daemon port
        intWebServicePort = self._portPrompt(
            'Enter port for local webservice daemon',
            self._settings['intWebServicePort'])

        return intWebPort, adminPort, intWebServicePort

    def _removePackageSources(self):
        pkgManager = self._osObjectFactory.getOsPackageManager()
        for pkgSrcName in pkgManager.getPackageSourceNames():
            self._logger.info(
                'Removing package source [%s]' % (pkgSrcName))
            pkgManager.removePackageSource(pkgSrcName)

    def _disableTortugaws(self):
        self.out('  * Disabling Tortuga webservice\n')

        _tortugaWsManager = self._osObjectFactory.getTortugawsManager()
        serviceName = _tortugaWsManager.getServiceName()
        _osServiceManager = getOsObjectFactory().getOsServiceManager()

        try:
            _osServiceManager.stop(serviceName)
        except CommandFailed:
            pass

    def cleanup(self):
        # If possible, remove any package sources we added
        self._removePackageSources()

        osUtility.removeFile(self._lockFilePath)

        osUtility.removeFile(self._cm.getProfileNiiFile())

        # Turn off the webservice daemon
        self._disableTortugaws()

        # Restore resolv.conf
        if osUtility.haveBackupFile('/etc/resolv.conf'):
            osUtility.restoreFile('/etc/resolv.conf')

        # Drop database
        dbManager = self._osObjectFactory.getOsApplicationManager(
            self._settings['database']['engine'])

        try:
            dbSchema = self._cm.getDbSchema()

            self.out('  * Removing database [%s]\n' % (dbSchema))

            dbManager.destroyDb(dbSchema)
        except Exception as ex:   # pylint: disable=broad-except
            self._logger.exception(
                'Could not destroy existing db: {}'.format(ex))

        # Remove DB password file
        osUtility.removeFile(self._cm.getDbPasswordFile())

        # Remove CFM secret
        cfmSecretFile = self._cm.getCfmSecretFile()
        if os.path.exists(cfmSecretFile):
            osUtility.removeFile(self._cm.getCfmSecretFile())

        # Generic cleanup
        osUtility.removeLink('/etc/tortuga-release')

        # Cleanup or remove depot directory
        errmsg = 'Removing contents of [%s]' % (self._settings['depotpath'])

        self._logger.debug(errmsg)

        if self._depotCreated:
            self.out('  * %s\n' % (errmsg))

            osUtility.removeDir(self._settings['depotpath'])
        else:
            if self._settings['depotpath']:
                self.out('  * %s\n' % (errmsg))

                tortugaSubprocess.executeCommand(
                    'rm -rf %s/*' % (self._settings['depotpath']))

                self.out('\n')

        if not self._forceCleaning:
            self.out('Consult log(s) for further details.\n')

            self._logger.error('Installation failed')

    def runSetup(self):
        """ Installer setup. """
        self.checkPreInstallConfiguration()

        # Do not run cleanup if this fails.
        self.startSetup()

        try:
            self.preInstallPrep()

            self.getClusterConfig()

            self.prepDepot()

            self.preConfig()

            self.pre_init_db()

            self.puppetBootstrap()

            dbm, session = self.initDatabase()

            try:

                self.createAdminUser(
                    session,
                    self._settings['adminUsername'],
                    self._settings['adminPassword'])

                self.installKits(dbm)

                self.enableComponents(session)
            finally:
                dbm.closeSession()

                self.puppetApply()

            self.out('\nTortuga installation completed successfully!\n\n')

            print('Run \"exec -l $SHELL\" to initialize Tortuga environment\n')
        except Exception:  # pylint: disable=broad-except
            self._logger.exception('Fatal error occurred during setup')

            raise TortugaException('Installation failed')

    def _generate_db_password(self):
        """
        Generate a database password.

        """
        #
        # Because Apache httpd server is not installed at the time this
        # runs, we cannot set the ownership of this file to be 'apache'
        # (which is necessary for the Tortuga webservice).
        #
        # Set ownership of file to root:puppet.
        #
        # When the Puppet bootstrap runs, it changes the ownership to
        # 'apache:puppet' and everybody is happy!
        #
        puppet_user = pwd.getpwnam('puppet')
        gid = puppet_user[3]
        self._generate_password_file(self._cm.getDbPasswordFile(), gid=gid)

    def _generate_redis_password(self):
        """
        Generate a password for Redis.

        """
        #
        # Puppet needs read access to this file so that it can use it for
        # writing the redis config file.
        #
        puppet_user = pwd.getpwnam('puppet')
        gid = puppet_user[3]
        self._generate_password_file(self._cm.getRedisPasswordFile(), gid=gid)

    def _generate_password_file(self, file_name: str,
                                password_length: int = 32,
                                uid: int = 0, gid: int = 0,
                                mode: int = 0o440):
        """
        Generate a password in a file.

        :param file_name:       the name of the file in which the password
                                will be stored
        :param password_length: the length of the password, default = 32
        :param uid:             the uid (owner) of the file, default = 0
        :param gid:             the gid (group) of the file, default = 0
        :param mode:            the file perms, default 0440

        """
        password = self._generate_password(password_length)

        with open(file_name, 'w') as fp:
            fp.write(password)

        os.chown(file_name, uid, gid)
        os.chmod(file_name, mode)

    def _generate_password(self, length: int = 8) -> str:
        """
        Generate a password.

        :param length: the length of the password

        :return:       the generated password

        """
        chars = string.ascii_letters + string.digits

        return ''.join([random.choice(chars) for _ in range(length)])

    def preConfig(self):
        # Create default hieradata directory
        hieraDataDir = '/etc/puppetlabs/code/environments/production/data'
        if not os.path.exists(hieraDataDir):
            os.makedirs(hieraDataDir)

        # Derive host name of puppet master from FQDN
        fqdn = self._settings['fqdn']

        configDict = {
            'version': 5,
            'DNSZone': 'private',
            'puppet_server': fqdn,
            'depot': self._settings['depotpath'],
        }

        with open(os.path.join(hieraDataDir, 'tortuga-common.yaml'),
                  'wb') as fp:
            fp.write(
                yaml.safe_dump(
                    configDict, explicit_start=True,
                    default_flow_style=False).encode())

        self._generate_db_password()
        self._generate_redis_password()

    def pre_init_db(self):
        # If using 'mysql' as the database backend, we need to install the
        # puppetlabs-mysql Puppet module prior to bootstrapping. This used
        # to be done in 'install-tortuga.sh'

        if self._settings['database']['engine'] == 'mysql':
            print('\nUsing MySQL as backing database.')

            puppet_module = 'puppetlabs-mysql'

            logmsg = f'Installing \'{puppet_module}\' module'

            self._logger.debug(logmsg)

            print(f'\n{logmsg}...', end='')

            cmd = ('/opt/puppetlabs/bin/puppet module install'
                   f' --color false {puppet_module}')
            tortugaSubprocess.executeCommand(cmd)

            print('done.')

    def puppetBootstrap(self):
        localPuppetRoot = os.path.join(self._cm.getEtcDir(), 'puppet')

        logFileName = '/tmp/bootstrap.log'

        puppet_server = self._settings['fqdn']

        # Bootstrap using Puppet
        cmd = ('/opt/puppetlabs/bin/puppet apply --verbose'
               ' --detailed-exitcodes'
               ' --execute "class { \'tortuga::installer\':'
               ' puppet_server => \'%s\','
               '}"' % (puppet_server)
               )

        retval = self._runCommandWithSpinner(
            cmd, '\nPerforming pre-configuration... Please wait...',
            logFileName=logFileName)

        if retval not in (0, 2):
            # Puppet can return a non-zero return code, even if it was
            # successful.
            self._logger.debug(
                'Puppet pre-configuration returned non-zero'
                ' return code [%d]' % (retval))

            errmsg = 'Puppet bootstrap failed (see log file %s)' % (
                logFileName)

            self._logger.error(errmsg)

            raise Exception(errmsg)

        self._logger.debug('Puppet pre-configuration completed')

    def initDatabase(self) -> Tuple[Any, Session]:
        msg = _('Initializing database')

        self._logger.info(msg)

        print_('\n' + msg + '... ', end='')

        # This cannot be a global import since the database configuration
        # may be set in this script.
        from tortuga.db.dbManager import DbManager

        dbm = DbManager()

        # create database
        dbm.init_database()

        session = dbm.openSession()

        # Prime the database previously created as part of the bootstrap
        try:
            dbUtility.primeDb(session, self._settings)

            dbUtility.init_global_parameters(session, self._settings)

            print_(_('done'))

            session.commit()
        except Exception as exc:  # pylint: disable=broad-except
            session.rollback()

            print_(_('failed.'))

            print_(_('Exception raised initializing database:') +
                   ' {0}'.format(exc), file=sys.stderr)

        self._logger.debug('Done initializing database')

        return dbm, session

    def installKits(self, dbm):
        self._logger.info('Installing kits')

        self.out('\n' + _('Installing kits') + '...\n')

        kitApi = KitApi()

        # Iterate over the glob of 'kits-*.tar.bz2'
        kitFileGlob = '%s/kits/kit-*.tar.bz2' % (self._cm.getRoot())

        # Split comma-separated list of kits to skip installing. Sorry, you
        # cannot skip installing the base kit.
        val = self._settings['skip_kits'] \
            if 'skip_kits' in self._settings else ''

        skip_kits = set([
            item for item in val.split(',') if item != 'base']) \
            if val else set()

        for kitPackage in glob.glob(kitFileGlob):
            try:
                kit = get_metadata_from_archive(kitPackage)
            except KitNotFound:
                msg = 'Kit [%s] is malformed/invalid. Skipping.' % (
                    os.path.basename(kitPackage))

                self._logger.error(msg)

                self.out('   %s\n' % (msg))

                continue

            if kit['name'] in skip_kits:
                msg = 'Kit [%s] installation skipped.' % (kit['name'])

                self.out('   %s\n' % (msg))

                self._logger.info(msg)

                continue

            try:
                kitApi.installKitPackage(dbm, kitPackage)
            except EulaAcceptanceRequired:
                msg = 'Kit [%s] requires EULA acceptance. Skipping.' % (
                    kitPackage)

                self.out('   %s\n' % (msg))

                self._logger.info(msg)

                continue

            self.out('   - %s installed.\n' % (kit['name']))

            self._logger.info('Kit [%s] installed' % (kit['name']))

        self._logger.info('Done installing kits')

        load_kits()

    def enableComponents(self, session: Session):
        """
        Raises:
            ConfigurationError
        """

        self._logger.info('Enabling \'installer\' component')

        base_kit = KitApi().getKit(session, 'base')

        enabledComponents = ['installer']

        # get list of components from 'base' kit
        components = [c for c in base_kit.getComponentList()
                      if c.getName() in enabledComponents]

        installerNode = NodeApi().getInstallerNode(session)

        for component in components:
            SoftwareProfileApi().enableComponent(
                session,
                installerNode.getSoftwareProfile().getName(),
                base_kit.getName(),
                base_kit.getVersion(),
                base_kit.getIteration(),
                component.getName(), compVersion=component.getVersion(),
            )

    def promptForAdminCredentials(self):
        # Get admin username and password for use with web service

        if self._settings['defaults']:
            self.out(_('\nUsing default Tortuga admin user name/password.\n'))

            return 'admin', 'password'

        username = password = None

        # Administrator username
        while True:
            username = self.prompt(
                'admin', 'admin',
                ['Enter name for Tortuga admin user.',
                 'This user is not associated with any system user.'],
                'Admin user name')

            if len(username) > 3:
                break

            self.out('Admin user name must be at least 4 characters.')

        # Administrator password
        while True:
            password = self.prompt(
                '', 'password',
                ['Enter password for Tortuga admin user.'],
                'Admin password', None, None, True)

            if len(password) < 4:
                self.out('Admin password must be at least 4 characters.')
                continue

            confirmPassword = self.prompt(
                '', 'password',
                ['Confirm admin password.'],
                'Confirm password', None, None, True)

            if confirmPassword == password:
                self.out('\n')
                break

            self.out('Passwords did not match.')

        return username, password

    def createAdminUser(self, session: Session, username, password):
        msg = _('Adding administrative user')

        self._logger.info(msg)

        self.out('\n' + msg + '... ')

        AdminApi().addAdmin(
            session,
            username, password, False,
            description='Added by tortuga-setup')

        self.out(_('done.') + '\n')
