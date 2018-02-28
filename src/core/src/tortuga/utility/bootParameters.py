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


def getBootParameters(hardwareProfile, softwareProfile):
    """ Given a hardware profile and a software profile return
        a dictionary of the kernel, kernelParams and initrd to use """

    # The hardwareProfile contains 3 PXE-related fields:
    #
    #   Kernel
    #   KernelParams
    #   Initrd
    #
    # The softwareProfile also contains these 3 fields, which will
    # only be used when 1) they contain a non-null value, and 2)
    # the hardwareProfile.softwareOverrideAllowed flag is True.

    kernel = hardwareProfile.kernel or ''
    kernelParams = hardwareProfile.kernelParams or ''
    initrd = hardwareProfile.initrd or ''

    if hardwareProfile.softwareOverrideAllowed:
        if softwareProfile.kernel:
            kernel = softwareProfile.kernel

        if softwareProfile.kernelParams:
            kernelParams = softwareProfile.kernelParams

        if softwareProfile.initrd:
            initrd = softwareProfile.initrd

    result = {
        'kernel': kernel,
        'kernelParams': kernelParams,
        'initrd': initrd,
    }

    return result
