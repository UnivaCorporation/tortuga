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

import os
import sys
import gettext
import socket
import time
import glob
import pwd
import random
import subprocess
import itertools
import configparser
import shutil
from six import print_
import yaml

from tortuga.config.configManager import ConfigManager
from tortuga.os_utility import osUtility
from tortuga.os_utility import tortugaSubprocess
from tortuga.helper.osHelper import getOsInfo
from tortuga.exceptions.softwareAlreadyDeployed \
    import SoftwareAlreadyDeployed
from tortuga.exceptions.invalidMachineConfiguration \
    import InvalidMachineConfiguration
from tortuga.os_utility.osUtility import getOsObjectFactory
from tortuga.deployer import dbUtility
from tortuga.exceptions.eulaAcceptanceRequired \
    import EulaAcceptanceRequired
from tortuga.admin.api import AdminApi
from tortuga.kit.kitApi import KitApi
from tortuga.exceptions.configurationError import ConfigurationError
from tortuga.softwareprofile.softwareProfileApi import SoftwareProfileApi
from tortuga.node.nodeApi import NodeApi
from tortuga.exceptions.commandFailed import CommandFailed
from tortuga.exceptions.invalidArgument import InvalidArgument
from tortuga.exceptions.kitNotFound import KitNotFound
from tortuga.kit.utils import getKitNameVersionIteration


class TortugaDeployer(object): \
        # pylint: disable=too-many-public-methods
    def __init__(self, logger, cmdline_options=None):
        self._cm = ConfigManager()

        self._logger = logger

        self._osObjectFactory = osUtility.getOsObjectFactory()

        self._settings = self.__load_settings(cmdline_options)

        self._settings['eulaAccepted'] = False

        self._settings['fqdn'] = self._getfqdn()

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

        self._osInfo = getOsInfo()

        self._logger.info('Detected OS: [%s]' % (self._osInfo))

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
            'engine': value if value else 'sqlite'
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

        activemq_enabled = cfg.getboolean('activemq', 'enable') \
            if cfg.has_section('activemq') and \
            cfg.has_option('activemq', 'enable') else True

        # ActiveMQ enabled
        settings['activemq'] = {
            'enable': activemq_enabled,
        }

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
        if len(args) > 0:
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
        if len(args) > 0:
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

            print ("To install Tortuga you must read and agree to "
                   "the following EULA.")

            print("Press 'Enter' to continue...")

            input('')
            os.system(cmd)
            print()
            while True:
                print('Do you agree? [Yes / No]', end=' ')
                answer = input('').lower()

                if answer not in ['yes', 'no', 'y', 'n']:
                    print ('Invalid response. Please respond \'Yes\''
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

    def prepSudo(self):
        """ Setup sudo. """

        self._logger.info('Setting up \'sudo\'')

        # TODO: these scripts have 'apache' hardcoded right now
        sysManager = self._osObjectFactory.getOsSysManager()
        sudoInitScript = sysManager.getSudoInitScript()
        p = tortugaSubprocess.executeCommandAndIgnoreFailure(sudoInitScript)
        self._logger.debug('sudo init output:\n%s' % p.getStdOut())

    def _runCommandWithSpinner(self, cmd, statusMsg, logFileName):
        self._logger.debug(
            '_runCommandWithSpinner(cmd=[%s], logFileName=[%s])' % (
                cmd, logFileName))

        self.out(statusMsg + '  ')

        # Open the log file in unbuffered mode
        fpOut = open(logFileName, 'wb', 0)

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
        except Exception as ex:   # pylint: disable=W0703
            self._logger.exception('Could not destroy existing db')

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

            self.initDatabase()

            self.createAdminUser(
                self._settings['adminUsername'],
                self._settings['adminPassword'])

            self.installKits()

            self._logger.debug('Enabling default components')

            self.enableComponents()

            self.prepSudo()

            self.puppetApply()

            self.out('\nTortuga installation completed successfully!\n\n')
        except Exception:
            self._logger.exception('Fatal error occurred during setup')

            self.out('\nInstallation failed...\n')

    def _generateDbPassword(self):
        '''
        Because Apache httpd server is not installed at the time this
        runs, we cannot set the ownership of this file to be 'apache'
        (which is necessary for the Tortuga webservice).

        Set ownership of file to root:puppet.

        When the Puppet bootstrap runs, it changes the ownership to
        'apache:puppet' and everybody is happy!
        '''

        dbPasswordFile = self._cm.getDbPasswordFile()

        puppetUser = pwd.getpwnam('puppet')
        gid = puppetUser[3]

        r = random.Random(time.time())

        # Generate random DB password
        chars = ('0123456789abcdefghijklmnopqrstuvwxyz'
                 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')

        password = ''.join([r.choice(chars) for _ in range(8)])

        if os.path.exists(dbPasswordFile):
            os.unlink(dbPasswordFile)

        # Write new db.passwd. Ownership would normally be 'root:puppet'
        # to allow Puppet master to use the password to configure mysqld.
        fp = os.open(dbPasswordFile, os.O_CREAT | os.O_WRONLY, 0o440)
        os.write(fp, password.encode())
        os.close(fp)

        os.chown(dbPasswordFile, 0, gid)

    def __append_hieradata(self, configDict):
        """Reflect Tortuga options to Hiera"""

        # ActiveMQ is enabled by default, only write setting if disabled
        if 'activemq' in self._settings and \
                'enable' in self._settings['activemq'] and \
                not self._settings['activemq']['enable']:
            configDict['tortuga::installer::activemq::enable'] = \
                self._settings['activemq']['enable']

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

        self.__append_hieradata(configDict)

        with open(os.path.join(hieraDataDir, 'tortuga-common.yaml'),
                  'wb') as fp:
            fp.write(
                yaml.safe_dump(
                    configDict, explicit_start=True,
                    default_flow_style=False).encode())

        self._generateDbPassword()

    def _getfqdn(self): \
            # pylint: disable=no-self-use
        # socket.getfqdn() may not return a fully-qualified host name
        reported_fqdn = socket.getfqdn()
        if '.' in reported_fqdn:
            return reported_fqdn

        # Attempt to append search domain
        search_domain = None

        with open('/etc/resolv.conf') as fp:
            for buf in fp.readlines():
                if buf.startswith('search'):
                    try:
                        search_domain = buf.split(' ', 1)[1].rstrip()
                    except IndexError:
                        # Malformed 'search' entry in resolv.conf
                        pass

        if search_domain:
            # Append search domain from resolv.conf
            return '%s.%s' % (reported_fqdn, search_domain)

        # Fallback to default behaviour...
        return reported_fqdn

    def pre_init_db(self):
        # If using 'mysql' as the database backend, we need to install the
        # puppetlabs-mysql Puppet module prior to bootstrapping. This used to
        # be done in 'install-tortuga.sh'

        if self._settings['database']['engine'] == 'mysql':
            logmsg = 'Installing \'puppetlabs-mysql\' module'

            self._logger.debug(logmsg)

            sys.stdout.write('\n' + logmsg + '... ')
            sys.stdout.flush()

            cmd = ('/opt/puppetlabs/bin/puppet module install'
                   ' --color false puppetlabs-mysql')
            tortugaSubprocess.executeCommand(cmd)

            sys.stdout.write('done.\n')

    def puppetBootstrap(self):
        localPuppetRoot = os.path.join(self._cm.getEtcDir(), 'puppet')

        logFileName = '/tmp/bootstrap.log'

        puppet_server = self._settings['fqdn']

        # Bootstrap using Puppet
        cmd = ('/opt/puppetlabs/bin/puppet apply --verbose'
               ' --config %s/bootstrap.puppet.conf'
               ' --modulepath'
               ' %s/modules:'
               '/etc/puppetlabs/code/environments/production/modules'
               ' --detailed-exitcodes'
               ' --execute "class { \'bootstrap\':'
               ' database_engine => \'%s\','
               ' activemq_enable => %s,'
               ' puppet_server => \'%s\','
               ' }"' % (localPuppetRoot, localPuppetRoot,
                        self._settings['database']['engine'],
                        str(self._settings['activemq']['enable']).lower(),
                        puppet_server))

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

    def initDatabase(self):
        msg = _('Initializing database')

        self._logger.info(msg)

        print_('\n' + msg + '... ', end='')

        # This cannot be a global import since the database configuration
        # may be set in this script.
        from tortuga.db.dbManager import DbManager

        dbm = DbManager()

        dbm.init_database()

        # Prime the database previously created as part of the bootstrap
        with dbm.session() as session:
            try:
                dbUtility.primeDb(
                    session, self._settings['fqdn'], self._osInfo,
                    self._settings)

                dbUtility.init_global_parameters(session, self._settings)

                print_(_('done'))

                session.commit()
            except Exception as exc:
                session.rollback()

                print_(_('failed.'))

                print_(_('Exception raised initializing database:') +
                       ' {0}'.format(exc), file=sys.stderr)

        self._logger.debug('Done initializing database')

    def installKits(self):
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
                kit = getKitNameVersionIteration(kitPackage)
            except KitNotFound:
                msg = 'Kit [%s] is malformed/invalid. Skipping.' % (
                    os.path.basename(kitPackage))

                self._logger.error(msg)

                self.out('   %s\n' % (msg))

                continue

            if kit[0] in skip_kits:
                msg = 'Kit [%s] installation skipped.' % (kit[0])

                self.out('   %s\n' % (msg))

                self._logger.info(msg)

                continue

            try:
                kitApi.installKitPackage(kitPackage)
            except EulaAcceptanceRequired:
                msg = 'Kit [%s] requires EULA acceptance. Skipping.' % (
                    kitPackage)

                self.out('   %s\n' % (msg))

                self._logger.info(msg)

                continue

            self.out('   - %s installed.\n' % (kit[0]))

            self._logger.info('Kit [%s] installed' % (kit[0]))

        self._logger.info('Done installing kits')

    def __getBaseKit(self): \
            # pylint: disable=no-self-use
        kitApi = KitApi()

        k = None

        for k in kitApi.getKitList():
            if k.getName() == 'base':
                break
        else:
            raise ConfigurationError(
                'Unable to find \"base\" kit. Check Tortuga installation')

        return k

    def enableComponents(self):
        """
        Raises:
            ConfigurationError
        """

        self._logger.info('Enabling \'installer\' component')

        k = self.__getBaseKit()

        enabledComponents = ['installer']

        components = [c for c in k.getComponentList()
                      if c.getName() in enabledComponents]

        installerNode = NodeApi().getInstallerNode()

        for component in components:
            SoftwareProfileApi().enableComponent(
                installerNode.getSoftwareProfile().getName(),
                k.getName(), k.getVersion(), k.getIteration(),
                component.getName(), component.getVersion(),
                sync=False)

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

    def createAdminUser(self, username, password):
        msg = _('Adding administrative user')

        self._logger.info(msg)

        self.out('\n' + msg + '... ')

        AdminApi().addAdmin(
            username, password, False,
            description='Added by tortuga-setup')

        self.out(_('done.') + '\n')
