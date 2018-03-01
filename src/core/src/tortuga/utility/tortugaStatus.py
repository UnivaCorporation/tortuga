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

TORTUGA_OK = 0
TORTUGA_ERROR = 1
TORTUGA_CONFIGURATION_ERROR = 2
TORTUGA_DB_ERROR = 3
TORTUGA_FILE_NOT_FOUND_ERROR = 4
TORTUGA_COMMAND_FAILED_ERROR = 5
TORTUGA_ABSTRACT_METHOD_ERROR = 6
TORTUGA_USER_NOT_AUTHORIZED_ERROR = 7
TORTUGA_INVALID_ARGUMENT_ERROR = 8
TORTUGA_KIT_NOT_FOUND_ERROR = 9
TORTUGA_KIT_ALREADY_EXISTS_ERROR = 10
TORTUGA_KIT_IN_USE_ERROR = 11
TORTUGA_INVALID_CLI_REQUEST_ERROR = 12
TORTUGA_OS_NOT_FOUND_ERROR = 13
TORTUGA_OS_ALREADY_EXISTS_ERROR = 14
TORTUGA_PARAMETER_NOT_FOUND_ERROR = 15
TORTUGA_PARAMETER_ALREADY_EXISTS_ERROR = 16
TORTUGA_NODE_NOT_FOUND_ERROR = 17
TORTUGA_NODE_ALREADY_EXISTS_ERROR = 18
TORTUGA_NIC_NOT_FOUND_ERROR = 21
TORTUGA_NIC_ALREADY_EXISTS_ERROR = 22
TORTUGA_NETWORK_NOT_FOUND_ERROR = 23
TORTUGA_NETWORK_ALREADY_EXISTS_ERROR = 24
TORTUGA_COMPONENT_NOT_FOUND_ERROR = 27
TORTUGA_COMPONENT_ALREADY_EXISTS_ERROR = 28
TORTUGA_UNSUPPORTED_OPERATING_SYSTEM_ERROR = 31
TORTUGA_PACKAGE_NOT_FOUND_ERROR = 32
TORTUGA_PACKAGE_ALREADY_EXISTS_ERROR = 33
TORTUGA_REMOTE_NOT_ALLOWED_ERROR = 34
TORTUGA_COMPONENT_ALREADY_ENABLED_ERROR = 35
TORTUGA_INVALID_INTEGRATION_MODULE_ERROR = 36
TORTUGA_REQUIRED_COMPONENT_NOT_ENABLED_ERROR = 37
TORTUGA_INVALID_CLUSTER_CONFIGURATION_ERROR = 38
TORTUGA_HARDWARE_PROFILE_ALREADY_EXISTS_ERROR = 39
TORTUGA_HARDWARE_PROFILE_NOT_FOUND_ERROR = 40
TORTUGA_HARDWARE_PROFILE_NETWORK_ALREADY_EXISTS_ERROR = 41
TORTUGA_HARDWARE_PROFILE_NETWORK_NOT_FOUND_ERROR = 42
TORTUGA_SOFTWARE_PROFILE_ALREADY_EXISTS_ERROR = 43
TORTUGA_SOFTWARE_PROFILE_NOT_FOUND_ERROR = 44
TORTUGA_SOFTWARE_PROFILE_COMPONENT_ALREADY_EXISTS_ERROR = 45
TORTUGA_SOFTWARE_PROFILE_COMPONENT_NOT_FOUND_ERROR = 46
TORTUGA_SOFTWARE_USES_HARDWARE_ALREADY_EXISTS_ERROR = 47
TORTUGA_SOFTWARE_USES_HARDWARE_NOT_FOUND_ERROR = 48
TORTUGA_NODE_SOFTWARE_PROFILE_LOCKED_ERROR = 49
TORTUGA_NODE_TRANSFER_NOT_VALID_ERROR = 50
TORTUGA_INVALID_APPLICATION_MODULE_ERROR = 51
TORTUGA_INTERNAL_ERROR = 52
TORTUGA_SOFTWARE_PROFILE_NOT_IDLE_ERROR = 53
TORTUGA_NODE_ALREADY_ACTIVE_ERROR = 54
TORTUGA_NODE_ALREADY_IDLE_ERROR = 55
TORTUGA_XML_RPC_FAILED_ERROR = 56
TORTUGA_NO_PARENT_NODE_ERROR = 57
TORTUGA_INVALID_PARTITION_SCHEME = 58
TORTUGA_INVALID_PROFILE_CREATION_TEMPLATE_ERROR = 59
TORTUGA_SOFTWARE_PROFILE_NOT_ACTIVE_ERROR = 60
TORTUGA_SOFTWARE_ALREADY_DEPLOYED_ERROR = 61
TORTUGA_INVALID_MACHINE_CONFIGURATION_ERROR = 62
TORTUGA_USER_ABORTED_ERROR = 63
TORTUGA_RULE_ALREADY_EXISTS_ERROR = 64
TORTUGA_RULE_NOT_FOUND_ERROR = 65
TORTUGA_INVALID_XML_ERROR = 66
TORTUGA_INVALID_MAC_ADDRESS = 67
TORTUGA_ADMIN_NOT_FOUND_ERROR = 68
TORTUGA_ADMIN_ALREADY_EXISTS_ERROR = 69
TORTUGA_IP_ALREADY_EXISTS_ERROR = 70
TORTUGA_NO_FREE_RESOURCES_AVAILABLE = 71
TORTUGA_URL_ERROR_ERROR = 72
TORTUGA_MISSING_RESPONSE_FILE_ENTRY = 73
TORTUGA_OS_NOT_SUPPORTED_ERROR = 74
TORTUGA_ANOTHER_INSTANCE_OWNS_LOCK_ERROR = 75
TORTUGA_EULA_REQUIRED_ERROR = 76
TORTUGA_RULE_ALREADY_ENABLED_ERROR = 77
TORTUGA_RULE_ALREADY_DISABLED_ERROR = 78
TORTUGA_RULE_DISABLED_ERROR = 79
TORTUGA_INVALID_ACTION_REQUEST_ERROR = 80
TORTUGA_PROFILE_MAPPING_NOT_ALLOWED = 81
TORTUGA_NETWORK_IN_USE_ERROR = 82
TORTUGA_DELETE_ADMIN_FAILED_ERROR = 83
TORTUGA_DELETE_NETWORK_FAILED_ERROR = 84
TORTUGA_UPDATE_SOFTWARE_PROFILE_FAILED_ERROR = 85
TORTUGA_UPDATE_HARDWARE_PROFILE_FAILED_ERROR = 86
TORTUGA_MAC_ADDRESS_ALREADY_EXISTS_ERROR = 87
TORTUGA_PARTITION_ALREADY_EXISTS_ERROR = 88
TORTUGA_PARTITION_NOT_FOUND_ERROR = 89
TORTUGA_INVALID_DB_RELATION_ERROR = 90
TORTUGA_INVALID_PROFILE_NAME_ERROR = 91
TORTUGA_UNSUPPORTED_OPERATION_ERROR = 92
TORTUGA_DELETE_PERSISTENT_VOLUME_ERROR = 93
TORTUGA_VOLUME_STILL_ATTACHED_ERROR = 94
TORTUGA_VOLUME_NOT_MAPPED_ERROR = 95
TORTUGA_VOLUME_DOES_NOT_EXIST_ERROR = 96
TORTUGA_VOLUME_ALREADY_MAPPED_ERROR = 97
TORTUGA_AUTHENTICATION_FAILED_ERROR = 98
TORTUGA_REMOTE_COMMUNICATION_FAILED_ERROR = 99
TORTUGA_MISSING_HYPERVISOR_NETWORK_ERROR = 103
TORTUGA_DELETE_NODE_FAILED_ERROR = 104
TORTUGA_CANNOT_MOUNT_KIT_MEDIA_ERROR = 105
TORTUGA_UNRECOGNIZED_KIT_MEDIA_ERROR = 106
TORTUGA_COPY_OS_MEDIA_ERROR = 107
TORTUGA_COPY_ERROR = 108
TORTUGA_FILE_ALREADY_EXISTS_ERROR = 109
TORTUGA_RESOURCE_ADAPTER_NOT_FOUND_ERROR = 110
TORTUGA_RESOURCE_ADAPTER_ALREADY_EXISTS_ERROR = 111
TORTUGA_INVALID_ACCEPT_TYPE = 112
TORTUGA_NETWORK_DEVICE_NOT_FOUND_ERROR = 113
TORTUGA_RESOURCE_ADAPTER_IN_USE_ERROR = 114
TORTUGA_HTTP_ERROR_ERROR = 115
TORTUGA_VIRTUAL_MACHINE_NOT_FOUND_ERROR = 116
TORTUGA_RESOURCE_NOT_FOUND_ERROR = 117
TORTUGA_RESOURCE_ALREADY_EXISTS_ERROR = 118
TORTUGA_OPERATION_FAILED_ERROR = 119
TORTUGA_NOT_FOUND_ERROR = 120
TORTUGA_UGE_CLUSTER_NOT_FOUND_ERROR = 121
TORTUGA_UGE_CLUSTER_ALREADY_EXISTS_ERROR = 122
TORTUGA_KIT_BUILD_ERROR = 123

exceptionMap = {
    TORTUGA_ERROR: 'exceptions.tortugaException.TortugaException',
    TORTUGA_CONFIGURATION_ERROR: 'exceptions.configurationError'
                                 '.ConfigurationError',
    TORTUGA_DB_ERROR: 'exceptions.dbError.DbError',
    TORTUGA_FILE_NOT_FOUND_ERROR: 'exceptions.fileNotFound.FileNotFound',
    TORTUGA_COMMAND_FAILED_ERROR: 'exceptions.commandFailed.CommandFailed',
    TORTUGA_ABSTRACT_METHOD_ERROR:
        'exceptions.abstractMethod.AbstractMethod',
    TORTUGA_USER_NOT_AUTHORIZED_ERROR:
        'exceptions.userNotAuthorized.UserNotAuthorized',
    TORTUGA_INVALID_ARGUMENT_ERROR:
        'exceptions.invalidArgument.InvalidArgument',
    TORTUGA_KIT_NOT_FOUND_ERROR: 'exceptions.kitNotFound.KitNotFound',
    TORTUGA_KIT_ALREADY_EXISTS_ERROR:
        'exceptions.kitAlreadyExists.KitAlreadyExists',
    TORTUGA_KIT_IN_USE_ERROR: 'exceptions.kitInUse.KitInUse',
    TORTUGA_INVALID_CLI_REQUEST_ERROR:
        'exceptions.invalidCliRequest.InvalidCliRequest',
    TORTUGA_OS_NOT_FOUND_ERROR: 'exceptions.osNotFound.OsNotFound',
    TORTUGA_OS_ALREADY_EXISTS_ERROR:
        'exceptions.osAlreadyExists.OsAlreadyExists',
    TORTUGA_PARAMETER_NOT_FOUND_ERROR:
        'exceptions.parameterNotFound.ParameterNotFound',
    TORTUGA_PARAMETER_ALREADY_EXISTS_ERROR:
        'exceptions.parameterAlreadyExists.ParameterAlreadyExists',
    TORTUGA_NODE_NOT_FOUND_ERROR: 'exceptions.nodeNotFound.NodeNotFound',
    TORTUGA_NODE_ALREADY_EXISTS_ERROR:
        'exceptions.nodeAlreadyExists.NodeAlreadyExists',
    TORTUGA_NIC_NOT_FOUND_ERROR: 'exceptions.nicNotFound.NicNotFound',
    TORTUGA_NIC_ALREADY_EXISTS_ERROR:
        'exceptions.nicAlreadyExists.NicAlreadyExists',
    TORTUGA_NETWORK_NOT_FOUND_ERROR:
        'exceptions.networkNotFound.NetworkNotFound',
    TORTUGA_NETWORK_ALREADY_EXISTS_ERROR:
        'exceptions.networkAlreadyExists.NetworkAlreadyExists',
    TORTUGA_COMPONENT_NOT_FOUND_ERROR:
        'exceptions.componentNotFound.ComponentNotFound',
    TORTUGA_COMPONENT_ALREADY_EXISTS_ERROR:
        'exceptions.componentAlreadyExists.ComponentAlreadyExists',
    TORTUGA_UNSUPPORTED_OPERATING_SYSTEM_ERROR:
        'exceptions.unsupportedOperatingSystem.UnsupportedOperatingSystem',
    TORTUGA_PACKAGE_NOT_FOUND_ERROR:
        'exceptions.packageNotFound.PackageNotFound',
    TORTUGA_PACKAGE_ALREADY_EXISTS_ERROR:
        'exceptions.packageAlreadyExists.PackageAlreadyExists',
    TORTUGA_REMOTE_NOT_ALLOWED_ERROR:
        'exceptions.remoteNotAllowed.RemoteNotAllowed',
    TORTUGA_COMPONENT_ALREADY_ENABLED_ERROR:
        'exceptions.componentAlreadyEnabled.ComponentAlreadyEnabled',
    TORTUGA_INVALID_INTEGRATION_MODULE_ERROR:
        'exceptions.invalidIntegrationModule.InvalidIntegrationModule',
    TORTUGA_REQUIRED_COMPONENT_NOT_ENABLED_ERROR:
        'exceptions.requiredComponentNotEnabled'
        '.RequiredComponentNotEnabled',
    TORTUGA_INVALID_CLUSTER_CONFIGURATION_ERROR:
        'exceptions.invalidClusterConfiguration'
        '.InvalidClusterConfiguration',
    TORTUGA_HARDWARE_PROFILE_ALREADY_EXISTS_ERROR:
        'exceptions.hardwareProfileAlreadyExists'
        '.HardwareProfileAlreadyExists',
    TORTUGA_HARDWARE_PROFILE_NOT_FOUND_ERROR:
        'exceptions.hardwareProfileNotFound.HardwareProfileNotFound',
    TORTUGA_HARDWARE_PROFILE_NETWORK_ALREADY_EXISTS_ERROR:
        'exceptions.hardwareProfileNetworkAlreadyExists'
        '.HardwareProfileNetworkAlreadyExists',
    TORTUGA_HARDWARE_PROFILE_NETWORK_NOT_FOUND_ERROR:
        'exceptions.hardwareProfileNetworkNotFound'
        '.HardwareProfileNetworkNotFound',
    TORTUGA_SOFTWARE_PROFILE_ALREADY_EXISTS_ERROR:
        'exceptions.softwareProfileAlreadyExists'
        '.SoftwareProfileAlreadyExists',
    TORTUGA_SOFTWARE_PROFILE_NOT_FOUND_ERROR:
        'exceptions.softwareProfileNotFound.SoftwareProfileNotFound',
    TORTUGA_SOFTWARE_PROFILE_COMPONENT_ALREADY_EXISTS_ERROR:
        'exceptions.softwareProfileComponentAlreadyExists'
        '.SoftwareProfileComponentAlreadyExists',
    TORTUGA_SOFTWARE_PROFILE_COMPONENT_NOT_FOUND_ERROR:
        'exceptions.softwareProfileComponentNotFound'
        '.SoftwareProfileComponentNotFound',
    TORTUGA_SOFTWARE_USES_HARDWARE_ALREADY_EXISTS_ERROR:
        'exceptions.softwareUsesHardwareAlreadyExists'
        '.SoftwareUsesHardwareAlreadyExists',
    TORTUGA_SOFTWARE_USES_HARDWARE_NOT_FOUND_ERROR:
        'exceptions.softwareUsesHardwareNotFound'
        '.SoftwareUsesHardwareNotFound',
    TORTUGA_NODE_SOFTWARE_PROFILE_LOCKED_ERROR:
        'exceptions.nodeSoftwareProfileLocked.NodeSoftwareProfileLocked',
    TORTUGA_NODE_TRANSFER_NOT_VALID_ERROR:
        'exceptions.nodeTransferNotValid.NodeTransferNotValid',
    TORTUGA_INVALID_APPLICATION_MODULE_ERROR:
        'exceptions.invalidApplicationModule.InvalidApplicationModule',
    TORTUGA_INTERNAL_ERROR: 'exceptions.internalError.InternalError',
    TORTUGA_SOFTWARE_PROFILE_NOT_IDLE_ERROR:
        'exceptions.softwareProfileNotIdle.SoftwareProfileNotIdle',
    TORTUGA_NODE_ALREADY_ACTIVE_ERROR:
        'exceptions.nodeAlreadyActive.NodeAlreadyActive',
    TORTUGA_NODE_ALREADY_IDLE_ERROR:
        'exceptions.nodeAlreadyIdle.NodeAlreadyIdle',
    TORTUGA_XML_RPC_FAILED_ERROR: 'exceptions.xmlRpcFailed.XmlRpcFailed',
    TORTUGA_NO_PARENT_NODE_ERROR: 'exceptions.noParentNode.NoParentNode',
    TORTUGA_INVALID_PARTITION_SCHEME:
        'exceptions.invalidPartitionScheme.InvalidPartitionScheme',
    TORTUGA_INVALID_PROFILE_CREATION_TEMPLATE_ERROR:
        'exceptions.invalidProfileCreationTemplate'
        '.InvalidProfileCreationTemplate',
    TORTUGA_SOFTWARE_PROFILE_NOT_ACTIVE_ERROR:
        'exceptions.softwareProfileNotActive.SoftwareProfileNotActive',
    TORTUGA_SOFTWARE_ALREADY_DEPLOYED_ERROR:
        'exceptions.softwareAlreadyDeployed.SoftwareAlreadyDeployed',
    TORTUGA_INVALID_MACHINE_CONFIGURATION_ERROR:
        'exceptions.invalidMachineConfiguration'
        '.InvalidMachineConfiguration',
    TORTUGA_USER_ABORTED_ERROR: 'exceptions.userAborted.UserAborted',
    TORTUGA_RULE_NOT_FOUND_ERROR: 'exceptions.ruleNotFound.RuleNotFound',
    TORTUGA_RULE_ALREADY_EXISTS_ERROR:
        'exceptions.ruleAlreadyExists.RuleAlreadyExists',
    TORTUGA_INVALID_XML_ERROR: 'exceptions.invalidXml.InvalidXml',
    TORTUGA_INVALID_MAC_ADDRESS:
        'exceptions.invalidMacAddress.InvalidMacAddress',
    TORTUGA_ADMIN_NOT_FOUND_ERROR:
        'exceptions.adminNotFound.AdminNotFound',
    TORTUGA_ADMIN_ALREADY_EXISTS_ERROR:
        'exceptions.adminAlreadyExists.AdminAlreadyExists',
    TORTUGA_IP_ALREADY_EXISTS_ERROR:
        'exceptions.ipAlreadyExists.IpAlreadyExists',
    TORTUGA_NO_FREE_RESOURCES_AVAILABLE:
        'exceptions.noFreeResourcesAvailable.NoFreeResourcesAvailable',
    TORTUGA_URL_ERROR_ERROR:
        'exceptions.urlErrorException.UrlErrorException',
    TORTUGA_MISSING_RESPONSE_FILE_ENTRY:
        'exceptions.missingResponseFileEntry.MissingResponseFileEntry',
    TORTUGA_OS_NOT_SUPPORTED_ERROR:
        'exceptions.osNotSupported.OsNotSupported',
    TORTUGA_ANOTHER_INSTANCE_OWNS_LOCK_ERROR:
        'exceptions.anotherInstanceOwnsLock.AnotherInstanceOwnsLock',
    TORTUGA_EULA_REQUIRED_ERROR:
        'exceptions.eulaAcceptanceRequired.EulaAcceptanceRequired',
    TORTUGA_RULE_ALREADY_ENABLED_ERROR:
        'exceptions.ruleAlreadyEnabled.RuleAlreadyEnabled',
    TORTUGA_RULE_ALREADY_DISABLED_ERROR:
        'exceptions.ruleAlreadyDisabled.RuleAlreadyDisabled',
    TORTUGA_RULE_DISABLED_ERROR: 'exceptions.ruleDisabled.RuleDisabled',
    TORTUGA_INVALID_ACTION_REQUEST_ERROR:
        'exceptions.invalidActionRequest.InvalidActionRequest',
    TORTUGA_PROFILE_MAPPING_NOT_ALLOWED:
        'exceptions.profileMappingNotAllowed.ProfileMappingNotAllowed',
    TORTUGA_NETWORK_IN_USE_ERROR: 'exceptions.networkInUse.NetworkInUse',
    TORTUGA_DELETE_ADMIN_FAILED_ERROR:
        'exceptions.deleteAdminFailed.DeleteAdminFailed',
    TORTUGA_DELETE_NETWORK_FAILED_ERROR:
        'exceptions.deleteNetworkFailed.DeleteNetworkFailed',
    TORTUGA_UPDATE_SOFTWARE_PROFILE_FAILED_ERROR:
        'exceptions.updateSoftwareProfileFailed'
        '.UpdateSoftwareProfileFailed',
    TORTUGA_UPDATE_HARDWARE_PROFILE_FAILED_ERROR:
        'exceptions.updateHardwareProfileFailed'
        '.UpdateHardwareProfileFailed',
    TORTUGA_MAC_ADDRESS_ALREADY_EXISTS_ERROR:
        'exceptions.macAddressAlreadyExists.MacAddressAlreadyExists',
    TORTUGA_PARTITION_ALREADY_EXISTS_ERROR:
        'exceptions.partitionAlreadyExists.PartitionAlreadyExists',
    TORTUGA_PARTITION_NOT_FOUND_ERROR:
        'exceptions.partitionNotFound.PartitionNotFound',
    TORTUGA_INVALID_DB_RELATION_ERROR:
        'exceptions.invalidDbRelation.InvalidDbRelation',
    TORTUGA_INVALID_PROFILE_NAME_ERROR:
        'exceptions.invalidProfileName.InvalidProfileName',
    TORTUGA_UNSUPPORTED_OPERATION_ERROR:
        'exceptions.unsupportedOperation.UnsupportedOperation',
    TORTUGA_DELETE_PERSISTENT_VOLUME_ERROR:
        'exceptions.deletePersistentVolumeFailed'
        '.DeletePersistentVolumeFailed',
    TORTUGA_VOLUME_STILL_ATTACHED_ERROR:
        'exceptions.volumeStillAttached.VolumeStillAttached',
    TORTUGA_VOLUME_NOT_MAPPED_ERROR:
        'exceptions.volumeNotMapped.VolumeNotMapped',
    TORTUGA_VOLUME_DOES_NOT_EXIST_ERROR:
        'exceptions.volumeDoesNotExist.VolumeDoesNotExist',
    TORTUGA_VOLUME_ALREADY_MAPPED_ERROR:
        'exceptions.volumeAlreadyMapped.VolumeAlreadyMapped',
    TORTUGA_AUTHENTICATION_FAILED_ERROR:
        'exceptions.authenticationFailed.AuthenticationFailed',
    TORTUGA_REMOTE_COMMUNICATION_FAILED_ERROR:
        'exceptions.remoteCommunicationFailed.RemoteCommunicationFailed',
    TORTUGA_MISSING_HYPERVISOR_NETWORK_ERROR:
        'exceptions.missingHypervisorNetwork.MissingHypervisorNetwork',
    TORTUGA_DELETE_NODE_FAILED_ERROR:
        'exceptions.deleteNodeFailed.DeleteNodeFailed',
    TORTUGA_CANNOT_MOUNT_KIT_MEDIA_ERROR:
        'exceptions.cannotMountKitMedia.CannotMountKitMedia',
    TORTUGA_UNRECOGNIZED_KIT_MEDIA_ERROR:
        'exceptions.unrecognizedKitMedia.UnrecognizedKitMedia',
    TORTUGA_COPY_OS_MEDIA_ERROR:
        'exceptions.copyOsMediaError.CopyOsMediaError',
    TORTUGA_COPY_ERROR: 'exceptions.copyError.CopyError',
    TORTUGA_FILE_ALREADY_EXISTS_ERROR:
        'exceptions.fileAlreadyExists.FileAlreadyExists',
    TORTUGA_RESOURCE_ADAPTER_NOT_FOUND_ERROR:
        'exceptions.resourceAdapterNotFound.ResourceAdapterNotFound',
    TORTUGA_RESOURCE_ADAPTER_ALREADY_EXISTS_ERROR:
        'exceptions.resourceAdapterAlreadyExists'
        '.ResourceAdapterAlreadyExists',
    TORTUGA_INVALID_ACCEPT_TYPE:
        'exceptions.invalidAcceptType.InvalidAcceptType',
    TORTUGA_NETWORK_DEVICE_NOT_FOUND_ERROR:
        'exceptions.networkDeviceNotFound.NetworkDeviceNotFound',
    TORTUGA_RESOURCE_ADAPTER_IN_USE_ERROR:
        'exceptions.resourceAdapterInUse.ResourceAdapterInUse',
    TORTUGA_HTTP_ERROR_ERROR:
        'exceptions.httpErrorException.HttpErrorException',
    TORTUGA_VIRTUAL_MACHINE_NOT_FOUND_ERROR:
        'exceptions.virtualMachineNotFound.VirtualMachineNotFound',
    TORTUGA_RESOURCE_NOT_FOUND_ERROR:
        'exceptions.resourceNotFound.ResourceNotFound',
    TORTUGA_RESOURCE_ALREADY_EXISTS_ERROR:
        'exceptions.resourceAlreadyExists.ResourceAlreadyExists',
    TORTUGA_OPERATION_FAILED_ERROR:
        'exceptions.operationFailed.OperationFailed',
    TORTUGA_NOT_FOUND_ERROR:
        'exceptions.notFound.NotFound',
    TORTUGA_KIT_BUILD_ERROR:
        'exceptions.kitBuildError.KitBuildError',
    TORTUGA_UGE_CLUSTER_NOT_FOUND_ERROR:
        'tortuga_kits.uge_8_5_4.exceptions.ugeClusterNotFound.UgeClusterNotFound',
    TORTUGA_UGE_CLUSTER_ALREADY_EXISTS_ERROR:
        'tortuga_kits.uge_8_5_4.exceptions.ugeClusterAlreadyExists.UgeClusterAlreadyExists',
}
