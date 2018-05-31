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

import os
import shutil
from typing import Dict, Optional

from tortuga.config.configManager import ConfigManager
from tortuga.db.componentDbApi import ComponentDbApi
from tortuga.db.globalParameterDbApi import GlobalParameterDbApi
from tortuga.db.kitDbApi import KitDbApi
from tortuga.db.nodeDbApi import NodeDbApi
from tortuga.db.softwareProfileDbApi import SoftwareProfileDbApi
from tortuga.exceptions.componentNotFound import ComponentNotFound
from tortuga.exceptions.kitNotFound import KitNotFound
from tortuga.helper import osHelper
from tortuga.kit.registry import get_kit_installer
from tortuga.objects.softwareProfile import SoftwareProfile
from tortuga.objects.tortugaObject import TortugaObjectList
from tortuga.objects.tortugaObjectManager import TortugaObjectManager
from tortuga.os_utility import osUtility
from tortuga.puppet import Puppet
from tortuga.types import Singleton
from tortuga.utility import validation


class SoftwareProfileManager(TortugaObjectManager, Singleton): \
        # pylint: disable=too-many-public-methods

    BASE_KIT_NAME = 'base'

    def __init__(self):
        super(SoftwareProfileManager, self).__init__()
        self._sp_db_api = SoftwareProfileDbApi()
        self._node_db_api = NodeDbApi()
        self._component_db_api = ComponentDbApi()
        self._global_param_db_api = GlobalParameterDbApi()
        self._kit_db_api = KitDbApi()
        self._config_manager = ConfigManager()

    def getSoftwareProfileList(self, tags=None):
        """Return all of the softwareprofiles with referenced components
        in this softwareprofile
        """

        results = self._sp_db_api.getSoftwareProfileList(tags=tags)

        for software_profile_obj in results:
            # load any available software profile metadata
            software_profile_obj.setMetadata(
                self.get_software_profile_metadata(
                    software_profile_obj.getName()))

        return results

    def getIdleSoftwareProfileList(self):
        """ Return all of the idle softwareprofiles """
        return self._sp_db_api.getIdleSoftwareProfileList()

    def setIdleState(self, softwareProfileName, state):
        """ Sets the  idle state of a softwareprofile """
        return self._sp_db_api.setIdleState(softwareProfileName, state)

    def addAdmin(self, softwareProfileName, adminUsername):
        """
        Add an admin as an authorized user.

            Returns:
                None
            Throws:
                TortugaException
                AdminNotFound
                SoftwareProfileNotFound
        """
        return self._sp_db_api.addAdmin(softwareProfileName, adminUsername)

    def deleteAdmin(self, softwareProfileName, adminUsername):
        """
        Remove an admin as an authorized user.

            Returns:
                None
            Throws:
                TortugaException
                AdminNotFound
                SoftwareProfileNotFound
        """
        return self._sp_db_api.deleteAdmin(softwareProfileName, adminUsername)

    def updateSoftwareProfile(self, softwareProfileObject):
        self.getLogger().debug(
            'Updating software profile: %s' % (
                softwareProfileObject.getName()))

        # First get the object from the db we are updating...
        existingProfile = self.\
            getSoftwareProfileById(softwareProfileObject.getId())

        # Set parameters that we will not allow updating
        softwareProfileObject.setOsInfo(existingProfile.getOsInfo())
        softwareProfileObject.setOsId(existingProfile.getOsId())
        softwareProfileObject.setIsIdle(existingProfile.getIsIdle())
        softwareProfileObject.setType(existingProfile.getType())

        self._sp_db_api.updateSoftwareProfile(softwareProfileObject)

    def getSoftwareProfile(
            self,
            name: str,
            optionDict: Optional[Dict[str, bool]] = None) -> SoftwareProfile:
        """
        Retrieve software profile by name

        """
        software_profile_obj = self._sp_db_api.getSoftwareProfile(
            name, optionDict=optionDict)

        # load any available software profile metadata
        software_profile_obj.setMetadata(
            self.get_software_profile_metadata(name))

        return software_profile_obj

    def getSoftwareProfileById(
            self,
            id_: int,
            optionDict: Optional[Dict[str, bool]] = None) -> SoftwareProfile:
        """
        Retrieve software profile by id

        """
        software_profile_obj = self._sp_db_api.getSoftwareProfileById(
            id_, optionDict=optionDict)

        # load any available software profile metadata
        software_profile_obj.setMetadata(
            self.get_software_profile_metadata(software_profile_obj.getName()))

        return software_profile_obj

    def _getCoreComponentForOsInfo(self, osInfo):
        # Find core component

        baseKit = None

        for baseKit in self._kit_db_api.getKitList():
            if not baseKit.getName() == self.BASE_KIT_NAME:
                continue

            break
        else:
            raise KitNotFound('Kit [%s] not found.' % (self.BASE_KIT_NAME))

        baseComp = None

        for baseComp in baseKit.getComponentList():
            if baseComp.getName() != 'core':
                continue

            break
        else:
            raise ComponentNotFound('Component [%s] not found in kit [%s]'
                                    % ('core', baseKit.getName()))

        comp = self._component_db_api.getBestMatchComponent(
            baseComp.getName(), baseComp.getVersion(), osInfo,
            baseKit.getId())

        comp.setKit(baseKit)

        return comp

    def _getOsInfo(self, bOsMediaRequired: bool):
        if not bOsMediaRequired:
            # As a placeholder, use the same OS as the installer

            # Find installer node entry
            node = self._node_db_api.getNode(
                ConfigManager().getInstaller(),
                {'softwareprofile': True})

            return node.getSoftwareProfile().getOsInfo()

        # Use available operating system kit; raise exception if
        # multiple available

        os_kits = self._kit_db_api.getKitList(os_kits_only=True)
        if not os_kits:
            raise KitNotFound('No operating system kit installed')

        if len(os_kits) > 1:
            raise KitNotFound(
                'Multiple OS kits defined; use --os option to specify'
                ' operating system')

        kit = self._kit_db_api.getKit(
            os_kits[0].getName(), os_kits[0].getVersion(), '0')

        components = kit.getComponentList()

        if not components:
            raise ComponentNotFound(
                'Malformed operating system kit [%s]' % (os_kits))

        osinfo_list = components[0].getOsInfoList()
        if len(osinfo_list) > 1:
            raise ComponentNotFound(
                'Multiple operating system components for kit [%s];'
                ' use --os argument to specify operating system' % (
                    os_kits[0]))

        return osinfo_list[0]

    def createSoftwareProfile(self, swProfileSpec, settingsDict=None):
        """
        Exceptions:
            ConfigurationError
            NetworkNotFound
            ComponentNotFound
            KitNotFound
            OSError
        """

        # Parse 'settingsDict'
        if settingsDict:
            # ... bOsMediaRequired; default is True
            bOsMediaRequired = settingsDict['bOsMediaRequired'] \
                if 'bOsMediaRequired' in settingsDict else True

            # ... unmanagedProfile; default is False
            unmanagedProfile = settingsDict['unmanagedProfile'] \
                if 'unmanagedProfile' in settingsDict else False

        # Validate software profile name
        validation.validateProfileName(swProfileSpec.getName())

        # Insert default description for software profile
        if swProfileSpec.getDescription() is None:
            swProfileSpec.setDescription(
                '%s Nodes' % (swProfileSpec.getName()))

        self.getLogger().debug(
            'Creating software profile [%s]' % (swProfileSpec))

        osInfo = swProfileSpec.getOsInfo() \
            if swProfileSpec.getOsInfo() else self._getOsInfo(bOsMediaRequired)

        # If we're creating an unmanaged software profile (no
        # DHCP/PXE/kickstart/OS) just create it now and we're done
        if unmanagedProfile:
            self._sp_db_api.addSoftwareProfile(swProfileSpec)
        else:
            if bOsMediaRequired and swProfileSpec.getOsInfo():
                try:
                    self._kit_db_api.getKit(
                        swProfileSpec.getOsInfo().getName(),
                        swProfileSpec.getOsInfo().getVersion(),
                        '0')
                except KitNotFound:
                    self._logger.error(
                        'OS kit for [%s] not found' % (
                            swProfileSpec.getOsInfo()))

                    raise
            else:
                swProfileSpec.setOsInfo(osInfo)

            # Get component manager for appropriate OS family
            osConfig = osHelper.getOsInfo(
                osInfo.getName(),
                osInfo.getVersion(),
                osInfo.getArch()
            )

            osObjFactory = osUtility.getOsObjectFactory(
                osConfig.getOsFamilyInfo().getName())

            # Need to be fancy with components
            spComponents = swProfileSpec.getComponents()
            swProfileSpec.setComponents(TortugaObjectList())

            bFoundOsComponent = False
            bFoundCoreComponent = False
            components = []

            # Iterate over components, adding them to the software profile
            for c in spComponents:
                cobj = self._component_db_api.getBestMatchComponent(
                    c.getName(),
                    c.getVersion(),
                    osInfo,
                    c.getKit().getId())

                k = cobj.getKit()

                if k.getIsOs():
                    # This component is a member of the OS kit, set the flag
                    bFoundOsComponent = True
                elif k.getName() == 'base' and c.getName() == 'core':
                    # Found the 'core' component in 'base' kit
                    bFoundCoreComponent = True

                components.append(cobj)

            # If the operating system is undefined for this software
            # profile, use the same OS as the installer.
            if bOsMediaRequired and not bFoundOsComponent:
                # Find OS component
                osCompName = '%s-%s-%s' % (osInfo.getName(),
                                           osInfo.getVersion(),
                                           osInfo.getArch())

                self.getLogger().debug(
                    'Automatically adding OS component [%s]'
                    ' (not specified in template)' % (osCompName))

                try:
                    osComponent = self._component_db_api.getComponent(
                        osCompName,
                        osInfo.getVersion(),
                        osInfo,
                        {'kit': True}
                    )

                    components.append(osComponent)
                except ComponentNotFound:
                    # Cannot find OS component, don't freak out
                    pass

            # Ensure 'core' component is enabled
            if not bFoundCoreComponent:
                # Attempt to automatically add the core component, only
                # if one exists for this OS

                try:
                    comp = self._getCoreComponentForOsInfo(osInfo)

                    self.getLogger().debug(
                        'Automatically adding [core] component'
                        ' (not specified in template)')

                    components.append(comp)
                except ComponentNotFound:
                    self.getLogger().warning(
                        'OS [{}] does not have a compatible \'core\''
                        ' component'.format(osInfo)
                    )

                # Initialize values for kernel, kernelParams, and initrd
                if not swProfileSpec.getKernel():
                    swProfileSpec.setKernel(
                        osObjFactory.getOsSysManager().getKernel(osInfo))

                if not swProfileSpec.getInitrd():
                    swProfileSpec.setInitrd(
                        osObjFactory.getOsSysManager().getInitrd(osInfo))

            # Add the software profile
            self._sp_db_api.addSoftwareProfile(swProfileSpec)

            # Enable components in one fell swoop
            for comp in components:
                self.getLogger().debug(
                    'Enabling component [%s]' % (comp.getName()))

                if comp.getKit().getIsOs():
                    # Don't use enableComponent() on OS kit
                    self._component_db_api.\
                        addComponentToSoftwareProfile(
                            comp.getId(), swProfileSpec.getId())

                    continue

                self.enableComponent(swProfileSpec.getName(),
                                     comp.getKit().getName(),
                                     comp.getKit().getVersion(),
                                     comp.getKit().getIteration(),
                                     comp.getName(),
                                     comp.getVersion())

            self.getLogger().debug(
                'Software profile [%s] created successfully' % (
                    swProfileSpec.getName()))

    def _getComponent(self, kit, compName, compVersion): \
            # pylint: disable=no-self-use
        # Iterate over component list, looking for a match
        comp = None

        for comp in kit.getComponentList():
            if comp.getName() == compName and \
                    comp.getVersion() == compVersion:
                break
        else:
            raise ComponentNotFound(
                "Component [%s-%s] not found in kit [%s]" % (
                    compName, compVersion, kit))

        return comp

    def _get_kit_by_component(self, comp_name, comp_version=None):
        """
        Gets a kit by compoent name/version.
        :param comp_name:    the name of the component
        :param comp_version: the version of the component

        :raises KitNotFound:
        :raises ComponentNotFound:

        """
        kit_list = self._kit_db_api.getKitList()
        kits = [
            kit
            for kit in kit_list
            for component in kit.getComponentList()
            if component.getName() == comp_name and
            (comp_version is None or
             component.getVersion() == comp_version)
        ]
        if not kits:
            raise KitNotFound(
                'Kit containing component [%s] not found' % (comp_name))

        if len(kits) > 1:
            raise ComponentNotFound(
                'Kit name must be specified, multiple kits contain '
                'component: {}'.format(comp_name)
            )

        return kits[0]

    def enableComponent(self, software_profile_name, kit_name, kit_version,
                        kit_iteration, comp_name, comp_version=None,
                        sync=True):
        """
        Enable a component on a software profile.

        :param software_profile_name: the name of the software profile
        :param kit_name:              the name of the kit
        :param kit_version:           the version of the kit
        :param kit_iteration:         the iteration of the kit
        :param comp_name:             the name of the component
        :param comp_version:          the version of the component

        :raises KitNotFound:
        :raises SoftwareProfileNotFound:
        :raises ComponentNotFound:

        """
        kit, comp_version = self._get_kit_and_component_version(
            kit_name, kit_version, kit_iteration, comp_name, comp_version)

        software_profile = self.getSoftwareProfile(software_profile_name,
                                                   {'os': True})

        if kit.getIsOs():
            best_match_component = self._enable_os_kit_component(
                kit, comp_name, comp_version, software_profile)
        else:
            best_match_component = self._enable_kit_component(
                kit, comp_name, comp_version, software_profile)

        if not best_match_component:
            self.getLogger().info(
                'Component not enabled: {}'.format(comp_name))
        else:
            self.getLogger().info(
                'Enabled component on software profile: {} -> {}'.format(
                    best_match_component, software_profile
                )
            )

            if sync:
                Puppet().agent()

    def _get_kit_and_component_version(self, kit_name, kit_version,
                                       kit_iteration, comp_name,
                                       comp_version=None):
        """
        Gets a Kit instance and component version.

        :param kit_name:      the name of the kit
        :param kit_version:   the version of the kit
        :param kit_iteration: the iteration of the kit
        :param comp_name:     the component name
        :param comp_version:  the component version (optional)

        :return: a tuple, consisting of (Kit, component_version)

        """
        kit = None
        if kit_name is None:
            kit = self._get_kit_by_component(comp_name,
                                             comp_version=comp_version)
            #
            # Get component version if required
            #
            if comp_version is None:
                for component in kit.getComponentList():
                    if component.getName() == comp_name:
                        comp_version = component.getVersion()
                        break
        elif kit_version is None or kit_iteration is None:
            kits_found = 0
            for k in self._kit_db_api.getKitList():
                if k.getName() == kit_name and \
                        (kit_version is None or
                         k.getVersion() == kit_version) and \
                        (kit_iteration is None or
                         k.getIteration() == kit_iteration):
                    kit = k
                    kits_found += 1

            if kits_found > 1:
                if kit_version is not None:
                    raise KitNotFound('Multiple kits found: {}-{}'.format(
                        kit_name, kit_version))
                else:
                    raise KitNotFound('Multiple kits found {}'.format(
                        kit_name))
        else:
            kit = self._kit_db_api.getKit(kit_name, kit_version,
                                          kit_iteration)

        return kit, comp_version

    def _enable_kit_component(self, kit, comp_name, comp_version,
                              software_profile):
        """
        Enables a regular kit component on a specific software profile.

        :param kit:              the Kit instance, whose component is being
                                 enabled
        :param comp_name:        the name of the component to enable
        :param comp_version:     the version of the component to enable
        :param software_profile: the software profile on which the component
                                 will be enabled

        :return:                 the Component instance that was enabled

        """
        kit_spec = (kit.getName(), kit.getVersion(), kit.getIteration())

        installer = get_kit_installer(kit_spec)()
        comp_installer = installer.get_component_installer(comp_name)
        if not comp_installer.is_enableable(software_profile):
            self.getLogger().warning(
                'Component cannot be enabled: {}'.format(
                    comp_installer.spec
                )
            )
            return None
        comp_installer.run_action('pre_enable', software_profile.getName())

        best_match_component = self._add_component_to_software_profile(
            kit, comp_name, comp_version, software_profile)

        comp_installer.run_action('enable', software_profile.getName())
        comp_installer.run_action('post_enable',
                                  software_profile.getName())

        return best_match_component

    def _enable_os_kit_component(self, kit, comp_name, comp_version,
                                 software_profile):
        """
        Enables an OS kit component on a specific software profile.

        :param kit:              the OS Kit instance, whose component is being
                                 enabled
        :param comp_name:        the name of the component to enable
        :param comp_version:     the version of the component to enable
        :param software_profile: the software profile on which the component
                                 will be enabled

        :return:                 the Component instance that was enabled

        """
        return self._add_component_to_software_profile(
            kit, comp_name, comp_version, software_profile)

    def _add_component_to_software_profile(self, kit, comp_name, comp_version,
                                           software_profile):
        """
        Adds a kit to a software profile. This is a data-only operation,
        as no pre/post enable actions are called.

        :param kit:              the OS Kit instance, whose component is being
                                 added
        :param comp_name:        the name of the component to add
        :param comp_version:     the version of the component to add
        :param software_profile: the software profile to which the component
                                 will be added

        :return:                 the Component instance that was added

        """
        best_match_component = \
            self._component_db_api.getBestMatchComponent(
                comp_name, comp_version, software_profile.getOsInfo(),
                kit.getId())
        self._component_db_api.addComponentToSoftwareProfile(
            best_match_component.getId(), software_profile.getId())

        return best_match_component

    def disableComponent(self, software_profile_name, kit_name, kit_version,
                         kit_iteration, comp_name, comp_version=None,
                         sync=True): \
            # pylint: disable=unused-argument
        """
        Disables a component on a software profile.

        :param software_profile_name: the name of the software profile
        :param kit_name:              the name of the kit
        :param kit_version:           the version of the kit
        :param kit_iteration:         the iteration of the kit
        :param comp_name:             the name of the component
        :param comp_version:          the version of the component

        :raises KitNotFound:
        :raises SoftwareProfileNotFound:
        :raises ComponentNotFound:

        """
        kit, comp_version = self._get_kit_and_component_version(
            kit_name, kit_version, kit_iteration, comp_name)

        software_profile = self.getSoftwareProfile(software_profile_name,
                                                   {'os': True})

        if kit.getIsOs():
            best_match_component = self._disable_os_kit_component(
                kit, comp_name, comp_version, software_profile)
        else:
            best_match_component = self._disable_kit_component(
                kit, comp_name, comp_version, software_profile)

        self.getLogger().info(
            'Disabled component on software profile: {} -> {}'.format(
                best_match_component, software_profile
            )
        )

        if sync:
            Puppet().agent()

    def _disable_kit_component(self, kit, comp_name, comp_version,
                               software_profile):
        """
        Disables a regular kit component on a specific software profile.

        :param kit:              the Kit instance, whose component is being
                                 disabled
        :param comp_name:        the name of the component to disable
        :param comp_version:     the version of the component to disable
        :param software_profile: the software profile on which the component
                                 will be disable

        :return:                 the Component instance that was disabled

        """
        kit_spec = (kit.getName(), kit.getVersion(), kit.getIteration())

        installer = get_kit_installer(kit_spec)()
        comp_installer = installer.get_component_installer(comp_name)
        comp_installer.run_action('pre_disable',
                                  software_profile.getName())
        comp_installer.run_action('disable',
                                  software_profile.getName())

        best_match_component = \
            self._remove_component_from_software_profile(
                kit, comp_name, comp_version, software_profile)

        comp_installer.run_action('post_disable',
                                  software_profile.getName())

        return best_match_component

    def _disable_os_kit_component(self, kit, comp_name, comp_version,
                                  software_profile):
        """
        Enables an OS kit component on a specific software profile.

        :param kit:              the OS Kit instance, whose component is being
                                 disabled
        :param comp_name:        the name of the component to disable
        :param comp_version:     the version of the component to disable
        :param software_profile: the software profile on which the component
                                 will be disabled

        :return:                 the Component instance that was disabled

        """
        return self._remove_component_from_software_profile(
            kit, comp_name, comp_version, software_profile)

    def _remove_component_from_software_profile(self, kit, comp_name,
                                                comp_version,
                                                software_profile):
        """
        Removes a kit to a software profile. This is a data-only operation,
        as no pre/post disable actions are called.

        :param kit:              the OS Kit instance, whose component is being
                                 removed
        :param comp_name:        the name of the component to remove
        :param comp_version:     the version of the component to remove
        :param software_profile: the software profile to which the component
                                 will be removed

        :return:                 the Component instance that was removed

        """
        best_match_component = self._component_db_api.getBestMatchComponent(
            comp_name, comp_version, software_profile.getOsInfo(),
            kit.getId())
        self._component_db_api.deleteComponentFromSoftwareProfile(
            best_match_component.getId(), software_profile.getId())

        return best_match_component

    def deleteSoftwareProfile(self, name):
        """
        Delete software profile by name

        Raises:
            SoftwareProfileNotFound
        """

        self._sp_db_api.deleteSoftwareProfile(name)

        # Remove all flags for software profile
        swProfileFlagPath = os.path.join(
            self._config_manager.getRoot(), 'var/run/actions/%s' % (name))
        if os.path.exists(swProfileFlagPath):
            shutil.rmtree(swProfileFlagPath)

        self.getLogger().info('Deleted software profile [%s]' % (name))

    def getNodeList(self, softwareProfileName):
        return self._sp_db_api.getNodeList(softwareProfileName)

    def getEnabledComponentList(self, name):
        """ Get the list of enabled components """
        return self._sp_db_api.getEnabledComponentList(name)

    def getPartitionList(self, softwareProfileName):
        """ Get list of partitions. """
        return self._sp_db_api.getPartitionList(softwareProfileName)

    def addUsableHardwareProfileToSoftwareProfile(self, hardwareProfileName,
                                                  softwareProfileName):
        self._logger.info(
            'Mapping hardware profile [%s] to software profile [%s]' % (
                hardwareProfileName, softwareProfileName))

        return self._sp_db_api.\
            addUsableHardwareProfileToSoftwareProfile(hardwareProfileName,
                                                      softwareProfileName)

    def deleteUsableHardwareProfileFromSoftwareProfile(
            self, hardwareProfileName, softwareProfileName):
        return self._sp_db_api.\
            deleteUsableHardwareProfileFromSoftwareProfile(
                hardwareProfileName, softwareProfileName)

    def copySoftwareProfile(self, srcSoftwareProfileName,
                            dstSoftwareProfileName):
        # Validate software profile name
        validation.validateProfileName(dstSoftwareProfileName)

        self._logger.info(
            'Copying software profile [%s] to [%s]' % (
                srcSoftwareProfileName, dstSoftwareProfileName))

        softwareProfile = self._sp_db_api.\
            copySoftwareProfile(srcSoftwareProfileName,
                                dstSoftwareProfileName)

        return softwareProfile

    def getUsableNodes(self, softwareProfileName):
        return self._sp_db_api.getUsableNodes(softwareProfileName)

    def get_software_profile_metadata(self, name: str) -> Dict[str, str]:
        """
        Call action_get_metadata() method for all kits
        """

        metadata = {}

        kits = self._kit_db_api.getKitList()

        for kit in kits:
            if kit.getIsOs():
                # ignore OS kits
                continue

            installer_ = get_kit_installer(
                (kit.getName(), kit.getVersion(), kit.getIteration()))

            # we are only interested in software profile metadata
            item = installer_().action_get_metadata(software_profile_name=name)
            if item:
                metadata.update(item)

        return metadata
