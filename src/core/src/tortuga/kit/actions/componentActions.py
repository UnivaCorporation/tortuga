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

# pylint: disable=no-self-use,no-member

import os.path
import traceback
import functools

from tortuga.kit.actions.actionsBase import ActionsBase
from tortuga.exceptions.configurationError import ConfigurationError
from tortuga.db.softwareProfileDbApi import SoftwareProfileDbApi


class ComponentActions(ActionsBase): \
        # pylint: disable=too-many-public-methods
    '''
    A component is an indivisible "feature" of an application;
    e.g., a telnet kit might contain a client component and a server component.

    These are the actions a component must perform on the Installer Node in
    the context of the NODE-GROUP-EDITOR command:

        enable          Invoked on the Installer Node when enabling the
                        component within a given softwareProfileName.

        disable         Invoked on the Installer Node when disabling the
                        component within a given softwareProfileName.

    These actions provides 3 hooks for a component to "hook-into" the
    action at various point:

        pre_<action>    Called before 'action', this provides the
                        component with an opportunity to make decisions
                        about the work to perform (when 'action' is
                        called), before actually doing any work. The
                        'pre' method is provided with a list of all the
                        components being invoked so that it may base
                        decisions in the context of the other components.

        <action>        The action.

        post_<action>   Called after 'action', this provides the component
                        with an opportunity to perform any post-processing.
                        The 'post' method is provided with a list of all
                        the components being invoked so that it may base
                        decisions in the context of the other components.

    Note that when processing a list of components, the 'pre' methods of
    all components are invoked first, followed by the 'action' methods
    of all components, finally the 'post' methods of all components.

    These are the actions a component must perform on the Installer Node in
    the context of the ADDHOST command:

        add_host        Invoked on the Installer Node when a new host is added
                        to the given softwareProfileName.

        delete_host     Invoked on the Installer Node when a host is deleted
                        from the given softwareProfileName.

    These are the actions a component must perform on the Installer Node in
    the context of the GENCONFIG command:

        configure       Invoked on the Installer Node when the component
                        may need to reconfigure itself within a given
                        softwareProfileName.

    These are the actions a component must perform on the Compute Node(s)
    in the context of the CFMCLIENT command:

        pre_install     Invoked on the Compute Node(s) before the native
                        package manager installs the component.

        post_install    Invoked on the Compute Node(s) after the native
                        package manager installs the component.  This would
                        be the likely place to start a service, if applicable.

        pre_remove      Invoked on the Compute Node(s) before the native
                        package manager removes the component.  This would
                        be the likely place to stop a service, if applicable.

        post_remove     Invoked on the Compute Node(s) after the native
                        package manager removes the component.

    A logger instance is also added to the base class so all derived components
    have a logger.
                _logger     A logger instance for creating log messages
    '''

    def __init__(self, kit):
        '''
        Arguments:
            cname       The name of the component as stored in the database.
                        If not given, defaults to the name of the class,
                        all lower case.

        Attributes:
            kit         The containing kit
        '''
        super(ComponentActions, self).__init__()

        if not hasattr(self, '__component_name__'):
            raise Exception(
                'Component class [{0}] does not have __component_name__ defined'.format(self.__class__.__name__))

        # Set by KitActions.add_component()
        self.kit = kit

    def getConfigFile(self):
        # Overridden from ActionsBase

        return os.path.join(self.kit.getConfigBase(),
                            '%s-component.conf' % (self.__component_name__)) \
            if self.kit else None

    def getLogger(self):
        return self._logger

    # NODE-GROUP-EDITOR Hooks (Installer Node)

    def pre_enable(self, softwareProfileName, *pargs, **kargs):
            # pylint: disable=unused-argument
        '''Invoked on the Installer Node before enabling the component'''
        self.__trace(*pargs, **kargs)

    def enable(self, softwareProfileName, *pargs, **kargs): \
            # pylint: disable=unused-argument
        '''Invoked on the Installer Node when enabling the component'''
        self.__trace(*pargs, **kargs)

    def post_enable(self, softwareProfileName, *pargs, **kargs): \
            # pylint: disable=unused-argument
        '''Invoked on the Installer Node after enabling the component'''
        self.__trace(*pargs, **kargs)

    def pre_disable(self, softwareProfileName, *pargs, **kargs): \
            # pylint: disable=unused-argument
        '''Invoked on the Installer Node before disabling the component'''
        self.__trace(*pargs, **kargs)

    def disable(self, softwareProfileName, *pargs, **kargs): \
            # pylint: disable=unused-argument
        '''Invoked on the Installer Node when disabling the component'''
        self.__trace(*pargs, **kargs)

    def post_disable(self, softwareProfileName, *pargs, **kargs): \
            # pylint: disable=unused-argument
        '''Invoked on the Installer Node after disabling the component'''
        self.__trace(*pargs, **kargs)

    def get_cloud_config(self, node, hwprofile, swprofile, user_data,
                         *pargs, **kargs): \
            # pylint: disable=unused-argument
        self.__trace(*pargs, **kargs)

    def pre_add_host(self, hwprofilename, swprofilename, hostname, ip,
                     *pargs, **kargs): \
            # pylint: disable=unused-argument
        '''
        This component action is typically called prior to committing new nodes
        to database. It is intended to be able to do operations such as
        updating DNS records prior to a bulk operation completing.
        '''
        self.__trace(*pargs, **kargs)

    def add_host(self, hardwareProfileName, softwareProfileName, nodes,
                 *pargs, **kargs): \
            # pylint: disable=unused-argument
        '''
        Invoked on the Installer Node when a new host is added to a
        software profile
        '''
        self.__trace(*pargs, **kargs)

    def pre_delete_host(self, hardwareProfileName, softwareProfileName, nodes,
                        *pargs, **kargs): \
            # pylint: disable=unused-argument
        '''
        Invoked on the Installer Node when a host is deleted from a
        software profile.
        '''
        self.__trace(*pargs, **kargs)

    def delete_host(self, hardwareProfileName, softwareProfileName, nodes,
                    *pargs, **kargs): \
            # pylint: disable=unused-argument
        '''
        Invoked on the Installer Node when a host is deleted from a
        software profile.
        '''
        self.__trace(*pargs, **kargs)

    def refresh(self, softwareProfiles, *pargs, **kargs): \
            # pylint: disable=unused-argument
        self.__trace(*pargs, **kargs)

    # GENCONFIG Hooks (Installer Node)

    def configure(self, softwareProfileName, *pargs, **kargs): \
            # pylint: disable=unused-argument
        '''Invoked on the Installer Node to configure the component'''
        self.__trace(*pargs, **kargs)

    def post_install(self, *pargs, **kargs):
        '''
        Invoked on the Compute Node(s) after the native package manager
        installs the component.

        This would be the likely place to start a service, if applicable.
        '''
        self.__trace(*pargs, **kargs)

    def pre_remove(self, *pargs, **kargs):
        '''
        Invoked on the Compute Node(s) before the native package manager
        removes the component.

        This would be the likely place to stop a service, if applicable.
        '''
        self.__trace(*pargs, **kargs)

    def post_remove(self, *pargs, **kargs):
        '''
        Invoked on the Compute Node(s) after the native package manager
        removes the component.
        '''
        self.__trace(*pargs, **kargs)

    # Private

    def __trace(self, *pargs, **kargs):
        stack = traceback.extract_stack()
        funcname = stack[-2][2]

        self._logger.debug('-- (pass) %s::%s %s %s' % (
            self.__class__.__name__, funcname, pargs, kargs))

    def get_puppet_args(self, dbSoftwareProfile, dbHardwareProfile): \
            # pylint: disable=unused-argument
        return {}


def installer_only(func):
    """Decorator function for Component.pre_enable() method to prevent
    enabling on a non-installer software profile
    """
    @functools.wraps(func)
    def pre_enable_wrapper(cls, softwareProfileName, *pargs, **kargs):
        swprofile = SoftwareProfileDbApi().getSoftwareProfile(
            softwareProfileName)
        if swprofile.getType() != 'installer':
            raise ConfigurationError(
                'Component [{0}] can only be enabled on Installer software'
                ' profile'.format(cls.__component_name__))

        return func(cls, softwareProfileName, *pargs, **kargs)

    return pre_enable_wrapper


def compute_only(func):
    """Decorator function for Component.pre_enable() method to prevent
    enabling on a non-compute software profile"""

    @functools.wraps(func)
    def pre_enable_wrapper(cls, softwareProfileName, *pargs, **kargs):
        swprofile = SoftwareProfileDbApi().getSoftwareProfile(
            softwareProfileName)
        if swprofile.getType() == 'installer':
            raise ConfigurationError(
                'Component [{0}] can only be enabled on compute software'
                ' profiles'.format(cls.__component_name__))

        return func(cls, softwareProfileName, *pargs, **kargs)

    return pre_enable_wrapper
