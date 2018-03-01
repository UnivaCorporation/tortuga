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

from tortuga.kit.installer import ComponentInstallerBase


#
# All component installer classes must be named ComponentInstaller in order
# to be automatically detected by the kits component detection logic.
#
class ComponentInstaller(ComponentInstallerBase):
    #
    # The name of your component. This name must be unique for the kit, but
    # it does not need to be unique across kits. I.e. it is fine for multiple
    # kits to have component with the same name.
    #
    name = 'mycomponent'

    #
    # The component version number. If you don't know what to put here, just
    # put the kit version number here instead.
    #
    version = '0.0.1'

    #
    # If this component is only designed to be enabled on installer nodes,
    # set this to True.
    #
    installer_only = False

    #
    # If this component is only designed to be enabled on compute nodes,
    # set this to True.
    #
    compute_only = False

    def action_pre_enable(self, software_profile_name, *args, **kwargs):
        """
        This hook is invoked on the installer prior to enabling the
        component on a software profile.

        :param software_profile_name: the name of the software profile on
                                      which the component is being enabled.
        :param args:
        :param kwargs:

        """
        pass

    def action_enable(self, software_profile_name, *args, **kwargs):
        """
        This hook is invoked on the installer when the component is enabled
        on a software profile.

        :param software_profile_name: the name of the software profile on
                                      which the component is being enabled.
        :param args:
        :param kwargs:

        """
        pass

    def action_post_enable(self, software_profile_name, *args, **kwargs):
        """
        This hook is invoked on the installer after the component has been
        enabled on a software profile.

        :param software_profile_name: the name of the software profile on
                                      which the component is being enabled.
        :param args:
        :param kwargs:

        """
        pass

    def action_pre_disable(self, software_profile_name, *args, **kwargs):
        """
        This hook is invoked on the installer prior to disabling it on a
        software profile.

        :param software_profile_name: the name of the software profile on
                                      which the component is being disabled.
        :param args:
        :param kwargs:

        """
        pass

    def action_disable(self, software_profile_name, *args, **kwargs):
        """
        This hook is invoked on the installer prior to disabling it on a
        software profile.

        :param software_profile_name: the name of the software profile on
                                      which the component is being disabled.
        :param args:
        :param kwargs:

        """
        pass

    def action_post_disable(self, software_profile_name, *args, **kwargs):
        """
        This hook is invoked on the installer after disabling it on a
        software profile.

        :param software_profile_name: the name of the software profile on
                                      which the component was disabled.
        :param args:
        :param kwargs:

        """
        pass

    def action_pre_add_host(self, hardware_profile, software_profile,
                            hostname, ip, *args, **kwargs):
        """
        This hook is invoked on the installer prior to adding a host with
        a software profile that has this component enabled.

        :param hardware_profile: the hardware profile of the host being added
        :param software_profile: the software profile of the host being added
        :param hostname:         the hostname of the host being added
        :param ip:               the ip address of the host being added
        :param args:
        :param kwargs:

        """
        pass

    def action_add_host(self, hardware_profile_name, software_profile_name,
                        nodes, *args, **kwargs):
        """
        This hook is invoked on the installer when adding a host with
        a software profile that has this component enabled.

        :param hardware_profile_name: the name of the hosts hardware profile
        :param software_profile_name: the name of the hosts software profile
        :param nodes:                 the nodes (hosts) added
        :param args:
        :param kwargs:

        """
        pass

    def action_pre_delete_host(self, hardware_profile, software_profile,
                               nodes, *args, **kwargs):
        """
        This hook is invoked on the installer piror to deleting a host with
        a software profile that has this component enabled.

        :param hardware_profile: the hardware profile
        :param software_profile: the software profile
        :param nodes:            the nodes (hosts) deleted
        :param args:
        :param kwargs:

        """
        pass

    def action_delete_host(self, hardware_profile_name, software_profile_name,
                           nodes, *args, **kwargs):
        """
        This hook is invoked on the installer when deleting a host with
        a software profile that has this component enabled.

        :param hardware_profile_name: the name of the hosts hardware profile
        :param software_profile_name: the name of the hosts software profile
        :param nodes:                 the nodes (hosts) deleted
        :param args:
        :param kwargs:

        """
        pass
