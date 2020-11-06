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

# See README.md for documentation on how to build Tortuga

import os
import subprocess
from paver.easy import path, task, call_task, sh, info


def get_git_revision():
    cmd = 'git rev-parse --short HEAD'

    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    result, _ = p.communicate()
    p.wait()

    return result.decode().rstrip()

version = '7.1.0+rev{}'.format(get_git_revision())

build_number = os.getenv('CI_PIPELINE_ID')
if build_number:
    version += '.{}'.format(build_number)

baseName = f'tortuga-{version}'


installRoot = path('install')
installDir = installRoot / path(baseName)
buildDir = path('build')
distDir = path('dist')

tarballFileName = path(baseName + '.tar.bz2')

tarballRootDir = path(baseName)

# All modules listed here are subdirectories under 'src' in the Tortuga
# source tree.  If these modules are to be included in the base install
# tarball, list them here.

defaultModules = [
    'core',
    'installer',
]

distKits = [
    'kit-base',
]

ignoreKits = [
    'kit-example'
]

requirements = 'requirements.txt'

with open(requirements) as fp:
    venv_packages = [buf.rstrip() for buf in fp.readlines()]


@task
def build(options):
    for defaultModule in defaultModules:
        cmd = 'python setup.py bdist_wheel'

        sh('cd src/%s && %s' % (defaultModule, cmd))

    if os.environ.get('TORTUGA_BUILD_DOCKER'):
        sh('docker run --rm=true -v $PWD/src/puppet/univa-tortuga:/root puppet/puppet-agent module build /root')
    else:
        sh('/opt/puppetlabs/pdk/bin/pdk build --force', cwd='src/puppet/univa-tortuga')

    for kit in distKits:
        cmd = 'tortuga kits build'
        sh('cd src/kits/{} && {}'.format(kit, cmd))

    # Copy dependencies into build directory
    call_task('install')

    # Create distribution tarball
    call_task('tarball')


@task
def dist(options):
    kit_dirs = path('src/kits/').dirs('kit-*')
    kits_built = []
    for kit_dir in kit_dirs:
        if kit_dir.name in distKits or kit_dir.name in ignoreKits:
            continue
        cmd = 'tortuga kits build'
        sh('cd {} && {}'.format(kit_dir, cmd))
        kits_built.append(kit_dir.name)
    _copyKits(kits_built, distDir)


def _copyKits(kitdirs, destdir):
    srcKitFiles = [
        path('src/kits/{}/dist'.format(defaultKit)).glob('*.tar.bz2')[0]
        for defaultKit in kitdirs
    ]

    if not len(srcKitFiles) == len(kitdirs):
        raise Exception('One or more kits missing; build is incomplete')

    if not srcKitFiles:
        return

    _instDir = path(destdir)

    if not _instDir.exists():
        _instDir.mkdir()

    # Take the first match only
    for srcKitFile in srcKitFiles:
        srcKitFile.copy(_instDir)


@task
def install(options):
    if not installDir.exists():
        installDir.makedirs()

    if not buildDir.exists():
        buildDir.mkdir()

    srcModuleFiles = [
        path('src/%s/dist' % (defaultModule)).glob('*.whl')[0]
        for defaultModule in defaultModules
    ]

    if len(srcModuleFiles) != len(defaultModules):
        raise Exception(
            'One or more modules are missing; build is incomplete')

    python_module_dir = installDir / path('python-tortuga')
    if not python_module_dir.exists():
        python_module_dir.makedirs()

    for f in srcModuleFiles:
        f.copy(python_module_dir)

    sh('dir2pi %s' % (python_module_dir))

    # Copy default kits
    _copyKits(distKits, installDir)

    # Copy 'tortuga' Puppet module
    for f in path('src/puppet/univa-tortuga/pkg').glob(
            'univa-tortuga-*.tar.gz'):
        f.copy(installDir)

    instScript = path('src/install-script/install-tortuga.sh')
    newPath = installDir.joinpath(instScript.basename())
    if not newPath.exists():
        instScript.link(newPath)


@task
def tarball(options):
    if not installDir.isdir():
        info('Please run \'paver install\' before tarball')

        return

    tarball = path.getcwd() / path('dist') / tarballFileName

    if tarball.exists():
        tarball.unlink()

    if not tarball.parent.exists():
        tarball.parent.mkdir()

    with installDir.parent:
        sh('tar cjf %s %s/' % (tarball, tarballRootDir))

    sh('ls -l dist/%s' % (tarballFileName))


@task
def clean(options):
    for kit in distKits:
        cmd = 'tortuga kits clean'
        sh('cd src/kits/{} && {}'.format(kit, cmd))

    for dir_name in ['build', 'dist', 'install']:
        sh('find . -type d -name {} -exec rm -r {{}} +'.format(dir_name))

    # remove puppet artifacts
    dirs = ['src/puppet', 'src/kits/kit-base/tortuga_kits/base*/puppet_modules']
    for puppet_dir_name in dirs:
        sh('find {} -type d -name pkg -exec rm -r {{}} +'.format(
            puppet_dir_name))
