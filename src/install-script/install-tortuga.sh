#!/bin/bash

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

cd $(dirname $0)

# set -o nounset
# set -o errexit

TORTUGA_ROOT=${TORTUGA_ROOT:-"/opt/tortuga"}

export TORTUGA_ROOT

VERBOSE=0
FORCE=0
DEBUG=0
enable_package_caching=1
download_only=0
force_hostname=0
readonly ucpkgcachedir="/tmp/tortuga_package_cache"


TEMP=$( getopt -o v,f --long force,verbose,debug,help,\
disable-package-caching,\
download-only,force-hostname,dependencies-dir: -n $(basename $0) -- "$@" )

if [ $? != 0 ]; then echo "Terminating..." >&2; exit 1; fi

eval set -- "$TEMP"

function usage() {
    echo
    echo "usage: $(basename $0) [options]"
    echo
    echo "Options:"
    echo
    echo "  --verbose|-v"
    echo "      Enable verbose output of this script"
    echo
    echo "  --force"
    echo "      Allow this script to run even if ${TORTUGA_ROOT} already exists"
    echo
    echo "  --disable-package-caching"
    echo "      Disable caching of dependent packages."
    echo
    echo "  --download-only"
    echo "      Download package dependencies only"
    echo
    echo "  --force-hostname"
    echo "      Ignore host name/FQDN sanity checks"
    echo
    echo "  --dependencies-dir=PATH"
    echo "      Path containing Tortuga installation dependencies"
    echo

    exit 0
}

while true; do
    case "$1" in
        -v|--verbose)
            VERBOSE=1
            shift
            ;;
        --debug)
            DEBUG=1
            shift
            ;;
        -f|--force)
            FORCE=1
            shift
            ;;
        -h|--help)
            usage
            shift
            ;;
        --disable-package-caching)
            enable_package_caching=0
            shift
            ;;
        --download-only)
            download_only=1
            shift;
            ;;
        --force-hostname)
            force_hostname=1
            shift;
            ;;
        --dependencies-dir)
            local_deps="$2"
            shift 2
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "Internal error!"
            exit 1
            ;;
    esac
done

puppet_args=""

# ensure color output is disabled if stdout is redirected
[[ -t 1 ]] || puppet_args="--color false"

# expect to find 'python-tortuga' in the Tortuga distribution tarball
[[ -d python-tortuga/simple ]] || {
    echo "Error: Tortuga distribution tarball is missing files" >&2
    exit 1
}

# get expanded path to Tortuga Python packages
local_tortuga_pip_repository=$(cd python-tortuga; pwd -P)

# ensure Tortuga Python package repository is included
pip_install_opts="--no-cache-dir \
--extra-index-url file://${local_tortuga_pip_repository}/simple"

[[ ${DEBUG} -eq 0 ]] && pip_install_opts+=" --quiet"

readonly INTWEBROOT="${TORTUGA_ROOT}/www_int"
readonly OFFLINEDEPS="${INTWEBROOT}/offline-deps"

# check if local dependencies directory was provided on command-line
[[ -n ${local_deps} ]] && {
    # Copy the offline dependencies to a standard location
    echo "* Copying installation dependencies from ${local_deps}"

    mkdir -p ${OFFLINEDEPS}

    readonly rsync_cmd="rsync --archive"

    ${rsync_cmd} ${local_deps}/ ${OFFLINEDEPS}

    mkdir -p ${INTWEBROOT}/3rdparty

    # copy 'mcollective-puppet-agent' tarball into expected location
    ${rsync_cmd} ${local_deps}/other/3rdparty/mcollective-puppet-agent/ \
        ${INTWEBROOT}/3rdparty/mcollective-puppet-agent/

    # Change the local_deps variable to point to the standard location
    local_deps="${OFFLINEDEPS}"

    # set directories to local dependencies
    local_pip_repository="${local_deps}/python"

    if [[ ! -d ${local_pip_repository} ]] || \
            [[ ! -d ${local_deps}/rpms ]]; then
        echo "Error: directory ${local_deps} does not contain required \
Tortuga dependencies" >&2
        exit 1
    fi

    echo "* Using Tortuga installation dependencies from ${local_deps}"

    pip_install_opts="--index-url file://${local_pip_repository}/simple \
${pip_install_opts}"

    # disable local package caching if dependencies available locally
    [[ -n ${local_deps} ]] && {
        enable_package_caching=0
        enable_epel=0
        enable_puppetlabs=0
    }

    # set up dependenices YUM repository
    cat >/etc/yum.repos.d/tortuga-deps.repo <<ENDL
[tortuga-deps]
name=Tortuga third-party dependencies
baseurl=file://${local_deps}/rpms
gpgcheck=0
enabled=1
ENDL
} || {
    enable_package_caching=1
    enable_epel=1
    enable_puppetlabs=1
}

[[ ${DEBUG} -eq 1 ]] || yum_common_args="--errorlevel 0 --debuglevel 0 --quiet"

pkgs=""

readonly basearch=$(arch)

function get_distro() {
    if type -P rpm &>/dev/null; then
        # rpm is installed, attempt to determine version
        if rpm --quiet -q centos-release; then
            dist="centos"
        elif rpm --quiet -q oraclelinux-release; then
            dist="oracle"
        elif rpm --quiet -q redhat-release-server; then
            dist="rhel"
        elif rpm --quiet -q redhat-release-workstation; then
            dist="rhel"
        else
            dist="unknown"
        fi
    else
        echo "Error: this system does not appear to be using RPM." >&2

        exit 1
    fi

    echo $dist
}

function get_distro_family() {
    if [[ $1 == centos ]] || [[ $1 == rhel ]] || [[ $1 == oracle ]]; then
        echo "rhel"
    else
        if [ $DEBUG -eq 1 ]; then
            echo "[debug] get_distro_family() returned 1"
        fi

        return 1
    fi
}

function get_dist_major_version() {
    case $1 in
        centos)
            relpkgname="centos-release"
            ;;
        oracle)
            relpkgname="oraclelinux-release"
            ;;
        rhel)
            relpkgname="redhat-release-server"

            if ! `pkgexists $relpkgname`; then
                # Check for "Workstation" installation
                relpkgname="redhat-release-workstation"
            fi
            ;;
        *)
            # Unable to determine Linux distribution
            return 1
            ;;
     esac

     # Attempt to extract the major version number
     if [[ $1 == centos ]]; then
         rpm --query --queryformat "%{VERSION}" $relpkgname
     else
         rpm -qi $relpkgname | awk '/^Version/ {print substr($3,0,1)}'
     fi
}

function get_dist_minor_version() {
    case $1 in
        centos)
            relpkgname="centos-release"
            ;;
        oracle)
            relpkgname="oraclelinux-release"
            ;;
        rhel)
            relpkgname="redhat-release-server"

            if ! pkgexists $relpkgname; then
                # Check for "Workstation" installation
                relpkgname="redhat-release-workstation"
            fi
            ;;
        *)
            # Unable to determine Linux distribution
            return 1
            ;;
    esac

    # Attempt to extract the major version number
    if [[ $1 == rhel ]]; then
        # "%{RELEASE}" in the RHEL release package shows major version and
        # minor version.
        rpm --query --queryformat "%{RELEASE}" $relpkgname | cut -f2 -d.
    else
        rpm --query --queryformat "%{RELEASE}" $relpkgname | cut -f1 -d.
    fi
}

function pkgexists() {
    # Check if package is installed
    if [[ $distro_family == rhel ]]; then
        rpm --query --quiet "${1}"
    else
        if [ $DEBUG -eq 1 ]; then
            echo "[debug] pkgexists(): unsupported distro \"${distro_family}\""
        fi

        return 0
    fi
}

function installpkg() {
    # Install the package
    pkgexists ${1} || yum install ${yum_common_args} \
--assumeyes ${1} >>/tmp/install-tortuga.log 2>&1
}

function install_epel() {
    local epelpkgname="epel-release"

    local epel_release_url="http://dl.fedoraproject.org/pub/epel/${epelpkgname}-latest-${distmajversion}.noarch.rpm"

    # Check if 'epel-release' package is already installed
    if pkgexists $epelpkgname; then return; fi

    echo "Installing ${epelpkgname}... " | tee -a /tmp/install-tortuga.log

    # Attempt to install 'epel-release' using default URL
    for ((i=0; i<5; i++)); do
        # Attempt to install 'epel-release'
        rpm --install --quiet ${epel_release_url} >>/tmp/install-tortuga.log 2>&1

        if [ $? -ne 0 ]; then continue; fi

        break
    done

    if ! pkgexists $epelpkgname; then
        echo "Error installing ${epelpkgname} (${epel_release_url}). Unable to proceed." | tee -a /tmp/install-tortuga.log
        exit 1
    fi
}

function check_puppet_memory() {
    local total_memory

    total_memory=$(free -g | grep "Mem:" | awk '{ print $2 }')

    if [ "$total_memory" -lt "2" ] && [ "$1" -lt "1" ]; then
        echo "Error: Puppet requires at least 2GB of memory" | tee -a /tmp/install-tortuga.log
        echo -e "\t ...ignore with --force"
        exit 1
    fi
}

function rpm_install() {
    for ((i=0; i < 5; i++)); do
        rpm --install --quiet ${1} 2>&1 | tee -a /tmp/install-tortuga.log
        [[ $? -ne 0 ]] && continue || break
    done
}

function install_puppetlabs_repo {
    local puppetlabspkgname="puppet5-release"

    # do not attempt to install 'puppet5-release' if already installed
    pkgexists ${puppetlabspkgname} || {
        rpm_install http://yum.puppetlabs.com/puppet5-release-el-${distmajversion}.noarch.rpm

        pkgexists ${puppetlabspkgname} || {
            echo "Error installing \"${puppetlabspkgname}\". Unable to proceed." >&2

            exit 1
        }
    }

    # install puppetlabs-release
    pkgexists puppetlabs-release || {
        rpm_install http://release-archives.puppet.com/yum/el/${distmajversion}/products/x86_64/puppetlabs-release-22.0-2.noarch.rpm
        sed -i 's,http://yum.puppetlabs.com,http://release-archives.puppet.com/yum,' /etc/yum.repos.d/puppetlabs.repo

        pkgexists puppetlabs-release || {
            echo "Error installing \"puppetlabs-release\". Unable to proceed." >&2
            exit 1
    }
    }
}

function cachepkgs {
    if [ -z "$*" ]; then return; fi

    local inst_pkgs=""
    local reinst_pkgs=""

    for pkg in $@; do
        if ! pkgexists $pkg; then
            # Package is not installed
            inst_pkgs="$inst_pkgs $pkg"
        else
            # Package is installed
            reinst_pkgs="$reinst_pkgs $pkg"
        fi
    done

    echo -n "Please wait... "

    [[ $download_only -ne 1 ]] && \
        echo -n "caching installation package dependencies... "

    local yum_dl_args

    yum_dl_args="${yum_common_args} --downloadonly --downloaddir=${ucpkgcachedir} --assumeyes"

    # packages that are not already installed on this host
    (
        [[ -n ${inst_pkgs} ]] && yum install ${yum_dl_args} ${inst_pkgs}

        # packages that are already installed
        [[ -n ${reinst_pkgs} ]] && yum reinstall ${yum_dl_args} ${reinst_pkgs}
    ) >>/tmp/install-tortuga.log 2>&1

    echo "done."

    update_pkg_cache "${ucpkgcachedir}"
}

function update_pkg_cache {
    {
        echo "--- createrepo BEGIN ---"

        createrepo "$1"

        echo "--- createrepo END ---"
    } >>/tmp/install-tortuga.log 2>&1
}

function installpkgs {
    [[ -n $@ ]] || return

    # Filter out list of packages that are already installed
    local tmppkg
    local pkglist=()

    for tmppkg in "$@"; do
        # ignore packages already installed
        pkgexists "${tmppkg}" && continue

        pkglist[${#pkglist[*]}]=$tmppkg
    done

    [ ${#pkglist[@]} -gt 0 ] || return

    local buf
    buf="${pkglist[*]}"

    echo "Installing packages: ${buf//  / }" | tee -a /tmp/install-tortuga.log

    local yum_install_opts

    # use local repository if package caching is enabled or local
    # dependencies repo has been specified
    [[ ${enable_package_caching} -ne 0 ]] && \
        yum_install_opts="--config /tmp/yum.tortuga.conf"

    local cmd="yum install ${yum_common_args} ${yum_install_opts} \
--assumeyes ${pkglist[*]}"

    {
        echo "yum command: ${cmd}"

        echo "--- yum BEGIN ---"

        $cmd

        echo "--- yum END ---"
    } >>/tmp/install-tortuga.log 2>&1
}

function install_yum_plugins() {
    local plugin_pkgname=""

    plugin_pkgname="yum-plugin-downloadonly"

    if yum --help 2>&1 | grep --quiet "downloadonly"; then
        # Plugin is present; do not attempt to install package
        return
    fi

    if ! pkgexists $plugin_pkgname; then
        installpkg $plugin_pkgname
        if [[ $? -ne 0 ]]; then
            echo "Error installing ${plugin_pkgname}. Check repository configuration and try again." | tee -a /tmp/install-tortuga.log
            echo "Unable to proceed!" | tee -a /tmp/install-tortuga.log
            exit 1
        fi
    fi
}

function disto_patches() {
    case $1 in
        oracle)
            installpkg yum-utils
            yum-config-manager -q --enable ol7_software_collections > /dev/null
            YUMCMD="$YUMCMD --skip-broken"
            ;;
    esac
}

is_puppet_module_installed() {
    /opt/puppetlabs/bin/puppet module list ${puppet_args} | grep --quiet "${1} "
}

install_puppet_module() {
    local install_args

    install_args="${puppet_args}"

    if [[ ${FORCE} -eq 1 ]] || [[ -n "${local_deps}" ]]; then
        install_args+=" --force"
    fi

    /opt/puppetlabs/bin/puppet module install ${install_args} $1
}

# Main script execution starts here

if [[ $TORTUGA_ROOT != /opt/tortuga ]]; then
    echo "Error: TORTUGA_ROOT must be set to /opt/tortuga for this release"

    exit 1
fi

if [[ -z "$TERM" ]]; then
    wrapwidth=$((`tput cols` - 5))
    [[ $wrapwidth -ge 80 ]] || wrapwidth=80
else
    wrapwidth=80
fi

# Perform hostname & FQDN sanity check
hostname=$(hostname)
fqdn=$(hostname --fqdn 2>/dev/null)
if [[ $? -ne 0 ]] || [[ -z $fqdn ]]; then
    errmsg="Error: Host name is unresolvable. Unable to proceed with Tortuga installation"

    echo $errmsg | fold -s --width=$wrapwidth

    exit 1
fi

# Attempt to extract the DNS suffix from the FQDN
suffix=$(echo $fqdn | cut -f2- -d".")

if [[ $hostname == localhost ]]; then
    errmsg="Error: \"localhost\" is an invalid host name for a Tortuga installer."

    echo $errmsg | fold -s --width $wrapwidth

    exit 1
fi

if [[ $download_only -eq 0 ]] && [[ $suffix == $hostname ]] && \
        [[ $force_hostname -eq 0 ]]; then
    errmsg="Error: using an unqualified host name can lead to potentially undesirable behaviour. Use --force-hostname option to override this check"

    echo $errmsg | fold -s --width $wrapwidth

    exit 1
fi

result=$(ping -c1 $fqdn 2>/dev/null)
if [ $? -eq 2 ]; then
    errmsg="Error: unable to resolve host name \"$hostname\". Unable to proceed with Tortuga installation."

    echo $errmsg | fold -s --width $wrapwidth

    exit 1
fi

ipaddress=$(echo $result | awk '/^PING/ {gsub(/[()]/, ""); print $3}')

if [[ $ipaddress == 127.0.0.1 ]]; then
    errmsg="Error: host name \"$hostname\" resolves to 127.0.0.1. This is invalid for a Tortuga installer."

    echo $errmsg | fold -s --width $wrapwidth

    exit 1
fi

# Begin installation here

if [[ $download_only -ne 1 ]]; then
    intromsg="Installing Tortuga to ${TORTUGA_ROOT}"
else
    intromsg="Caching Tortuga package dependencies..."
fi

echo ">>>>> $intromsg ($(date))" >>/tmp/install-tortuga.log

[[ ${FORCE} -eq 1 ]] && {
    echo "--force argument specified." | tee -a /tmp/install-tortuga.log
}

# This is the first output to the console (and log file)
echo $intromsg

if [[ $download_only -ne 1 ]] && [[ -d $TORTUGA_ROOT ]] && [[ $FORCE -ne 1 ]] && [[ -z "${local_deps}" ]]; then
    echo "Installation directory $TORTUGA_ROOT exists" | tee -a /tmp/install-tortuga.log
    echo
    echo "Use --force to force (re)installation"
    echo
    echo "--force not specified; exiting" >> /tmp/install-tortuga.log

    exit 1
fi

dist=$(get_distro)
if [ $? -ne 0 ]; then
    exit 1
fi

distro_family=$(get_distro_family "${dist}")
if [ $? -ne 0 ]; then
    echo "Error: unsupported distribution \"${dist}\"" | tee -a /tmp/install-tortuga.log
    exit 1
fi

# Check for RHEL major version
distmajversion=$(get_dist_major_version "${dist}")
[[ $? -eq 0 ]] || {
    echo "Error: unable to determine Linux distribution" | tee -a /tmp/install-tortuga.log

    exit 1
}

# Get minor version
distminversion=$(get_dist_minor_version $dist)
if [ $? -ne 0 ]; then
    echo "Error: unable to determine Linux distribution" | tee -a /tmp/install-tortuga.log
    exit 1
fi

# Output debug information to the log only
{
    echo "Detected distribution: ${dist}"
    echo "Detected distribution family: ${distro_family}"
    echo "Detected distribution major version: ${distmajversion}"
    echo "Detected distribution minor version: ${distminversion}"
} >>/tmp/install-tortuga.log

# Install 'createrepo', if necessary
pkgexists createrepo || {
    installpkg createrepo
    if [ $? -ne 0 ]; then
        echo "Error installing createrepo. Check repository configuration and try again." | tee -a /tmp/install-tortuga.log
        echo "Unable to proceed!" | tee -a /tmp/install-tortuga.log
        exit 1
    fi
}

# Create temporary package cache dir
if [[ $enable_package_caching -eq 1 ]]; then
    echo "Using temporary directory $ucpkgcachedir for package cache" >> /tmp/install-tortuga.log

    [[ ${FORCE} -eq 1 ]] && {
        echo "Removing directory \"${ucpkgcachedir}\"" | tee -a /tmp/install-tortuga.log

        rm -rf $ucpkgcachedir
    }

    [[ -d $ucpkgcachedir ]] || mkdir -p $ucpkgcachedir

    # Initialize the newly created (empty) directory as a valid repository
    update_pkg_cache $ucpkgcachedir

    # Create temporary yum.conf which includes local package cache
    cp /etc/yum.conf /tmp/yum.tortuga.conf

    cat >>/tmp/yum.tortuga.conf <<ENDL
[tortuga-local-cache]
name=tortuga-local-cache
baseurl=file://${ucpkgcachedir}
enabled=1
ENDL
fi

# Apply any patches needed for specific distribution
disto_patches $dist

# Check for SELinux
if type -P getenforce >/dev/null 2>&1; then
    sestatus=$(getenforce)
    if [[ $sestatus != Disabled ]] && [[ $sestatus != Permissive ]]; then
        echo
        echo "Error: Tortuga requires that SELinux is disabled or in permissive mode."
        echo
        echo "Please adjust operating system setting in /etc/sysconfig/selinux and/or kernel parameters and restart the installation." | fold -sw $wrapwidth
        exit 1
    fi
fi

# Check for 'yum-plugin-downloadonly'
[[ $distro_family == rhel ]] && install_yum_plugins

# Check for curl
if ! type -P curl >/dev/null 2>&1; then
    echo "Installing curl..."
    installpkg curl
    if [ $? -ne 0 ]; then
        echo "Error installing curl. Check repository configuration and try again" | tee -a /tmp/install-tortuga.log
        echo "Unable to proceed!" | tee -a /tmp/install-tortuga.log
        exit 1
    fi
fi

# Check there's enough memory for Puppet
check_puppet_memory $FORCE

# install epel repository
[[ ${distro_family} == rhel ]] && [[ $enable_epel -ne 0 ]] && install_epel

# Install puppetlabs repo
[[ ${enable_puppetlabs} -ne 0 ]] && install_puppetlabs_repo

# 'pkgs' is a list of packages to be installed on the Tortuga installer
# 'cachedpkgs' are cached for use by on-prem nodes

# these packages are installed locally and cached
commonpkgs="\
rh-python36 \
rh-python36-runtime \
rh-python36-python \
rh-python36-python-pip \
rh-python36-python-libs \
rh-python36-python-devel \
rh-python36-python-setuptools \
rh-python36-python-virtualenv \
"

# Packages common to all RHEL versions
pkgs="\
git \
puppetserver \
rsync \
"

# Packages cached for all RHEL versions
cachedpkgs="\
puppet-agent \
"

pkgs+=" ${commonpkgs}"
cachedpkgs+=" ${commonpkgs}"

# only install 'centos-release-scl' when running normal installation
[[ -z "${local_deps}" ]] && [[ ${dist} == centos ]] && {
    echo "Installing SCL repository... "
    installpkg centos-release-scl
    [[ $? -eq 0 ]] || {
        echo "Error installing \"centos-release-scl\". Unable to proceed." >&2
        exit 1
    }
}

# download packages to local cache
[[ $enable_package_caching -ne 0 ]] && cachepkgs ${commonpkgs}

# Create Tortuga internal webroot
[[ -d $INTWEBROOT/3rdparty ]] || mkdir -p "$INTWEBROOT/3rdparty"

[[ -d ${INTWEBROOT}/3rdparty/mcollective-puppet-agent ]] || \
    mkdir -p ${INTWEBROOT}/3rdparty/mcollective-puppet-agent
[[ -z ${local_deps} ]] && {
    # Download mcollective-puppet-agent plugin
    echo -n "Downloading 'mcollective-puppet-agent' plugin... "

    url=https://github.com/puppetlabs/mcollective-puppet-agent/archive/1.13.1.tar.gz

    ( cd ${INTWEBROOT}/3rdparty/mcollective-puppet-agent; \
        curl --retry 10 --retry-max-time 60 --silent --fail --location \
        --remote-name ${url} 2>&1 | tee -a /tmp/install-tortuga.log )

    [[ $? -eq 0 ]] || {
    echo "failed."
        echo
        echo "Error retrieving mcollective-puppet-agent. Unable to proceed" >&2

        exit 1
    }

    echo "done."
}

[[ "${download_only}" -eq 1 ]] && {
    # Force next Puppet run to synchronize newly downloaded packages
    echo "Done."

    exit 0
}

# install all (local) packages

installpkgs ${pkgs}

# Create Puppet modules directory, as necessary
echo "Installing Puppet modules" | tee -a /tmp/install-tortuga.log

# Install stdlib module from puppetlabs

if [[ ${FORCE} -eq 1 ]] || ! is_puppet_module_installed puppetlabs-stdlib; then
    echo "Installing puppetlabs-stdlib Puppet module..."

    if [[ -n "${local_deps}" ]]; then
        puppet_module_src="${local_deps}/puppet/puppetlabs-stdlib-4.25.1.tar.gz"
    else
        puppet_module_src="puppetlabs-stdlib"
    fi

    install_puppet_module ${puppet_module_src}
    [[ $? -eq 0 ]] || {
        echo "Error installing Puppet module \"puppetlabs-stdlib\"" | \
            tee -a /tmp/install-tortuga.log

        exit 1
    }
fi

is_puppet_module_installed univa-tortuga || {
    echo "Installing Tortuga Puppet integration module..." | tee -a /tmp/install-tortuga.log
    install_puppet_module univa-tortuga-*.tar.gz
    [[ $? -eq 0 ]] || {
        echo "Installation failed... unable to proceed" | tee -a /tmp/install-tortuga.log
        exit 1
    }
}

# source SCL Python 3.6 environment
. /opt/rh/rh-python36/enable

# Setup virtualenv (creates $TORTUGA_ROOT)
readonly virtualenv="python3 -m venv --system-site-packages"

echo -n "Setting up ${TORTUGA_ROOT} virtualenv... " | tee -a /tmp/install-tortuga.log
$virtualenv $TORTUGA_ROOT >>/tmp/install-tortuga.log 2>&1
if [ $? -ne 0 ]; then
    echo "failed"
    echo "Error creating Python virtualenv in ${TORTUGA_ROOT}" | tee -a /tmp/install-tortuga.log
    exit 1
fi

echo "done."

# Tortuga pre-installation
echo "Performing Tortuga pre-installation... " | \
    tee -a /tmp/install-tortuga.log

pip_install_cmd="${TORTUGA_ROOT}/bin/pip install ${pip_install_opts}"

# Upgrade pip
${pip_install_cmd} --upgrade pip==19.0.3 >>/tmp/install-tortuga.log 2>&1

[[ -n ${local_deps} ]] && {
    # Install pip2pi manually so that tortuga-core does not try to
    # download it from the internet
    ${pip_install_cmd} pip2pi >>/tmp/install-tortuga.log 2>&1
}

# Install Tortuga Python packages
for module in tortuga-core tortuga-installer; do
    echo -n "Installing ${module} Python package... " | \
        tee -a /tmp/install-tortuga.log

    ${pip_install_cmd} ${module} >>/tmp/install-tortuga.log 2>&1
    [[ $? -eq 0 ]] || {
        echo "failed."

        echo

        echo "Check /tmp/install-tortuga.log for errors" >&2

        exit 1
   }

   echo "done."
done

# copy Tortuga Python package repository
rsync -av "${local_tortuga_pip_repository}/" "${INTWEBROOT}/python-tortuga" \
    >>/tmp/install-tortuga.log 2>&1
[[ $? -eq 0 ]] || {
    echo "Error copying from \"${local_deps}/python-tortuga\" to \"${INTWEBROOT}/python-tortuga\"" >&2

    echo >&2

    echo "Installation failed." >&2

    exit 1
}

# Copy Puppet Hiera configuration
readonly hiera_data_dir="/etc/puppetlabs/code/environments/production/data"
readonly hieracfg="/etc/puppetlabs/code/environments/production/hiera.yaml"

# Backup 'hiera.yaml' included with 'puppet-agent' package
[[ -f ${hieracfg} ]] && {
    mv "${hieracfg}" "${hieracfg}.orig"
    [[ $? -eq 0 ]] || {
        echo "Error: unable to move \"${hieracfg}\" to \"${hieracfg}.orig\"" >&2
        exit 1
    }
}

# Copy customized 'hiera.yaml' in place
cp "${TORTUGA_ROOT}/etc/puppet/hiera.yaml" "${hieracfg}"
[[ $? -eq 0 ]] || {
    echo "Error copying \"${TORTUGA_ROOT}/etc/puppet/hiera.yaml\" to \"${hieracfg}\"" >&2
    exit 1
}

mkdir -p ${hiera_data_dir}

cp "${TORTUGA_ROOT}/etc/puppet/tortuga-extra.yaml" "${hiera_data_dir}"
[[ $? -eq 0 ]] || {
    echo "Error copying \"${TORTUGA_ROOT}/etc/puppet/tortuga-extra.yaml\" to \"${hiera_data_dir}\"" >&2
    exit 1
}

kitsdir="${TORTUGA_ROOT}/kits"

mkdir -p "${kitsdir}"

echo "Copying default kits to ${kitsdir}... "

find . -maxdepth 1 -type f -name 'kit-*.tar.bz2' | while read filename; do
    echo -n "   $(basename "${filename}")... "
    cp -f "${filename}" "${kitsdir}"
    echo "done."
done

[[ $enable_package_caching -eq 1 ]] || [[ -n ${local_deps} ]] && {
    # Copy cached packages from temporary directory to proper location
    echo -n "Synchronizing cached packages for use by compute nodes... " | tee -a /tmp/install-tortuga.log

    dstdir=$TORTUGA_ROOT/repos/3rdparty/$distro_family/$distmajversion/$basearch

    mkdir -p "${dstdir}"

    [[ ${enable_package_caching} -ne 0 ]] && srcdir=${ucpkgcachedir} || srcdir="${local_deps}/rpms"

    # We only want the output from this rsync to appear in the log file, not
    # on the console.
    rsync -av "${srcdir}/" "${dstdir}/" >>/tmp/install-tortuga.log 2>&1

    [[ $? -ne 0 ]] && {
        echo " failed."
        echo
        echo "Error copying cached packages; check free disk space"

        exit 1
    } | tee -a /tmp/install-tortuga.log

    echo "done." | tee -a /tmp/install-tortuga.log
}

# update 'tortuga.ini' to indicate offline installation mode
[[ -n "${local_deps}" ]] && {
    cat >>"${TORTUGA_ROOT}/config/tortuga.ini" <<ENDL
[installer]
offline_installation = true
ENDL

    echo "Creating empty OS media repository for off-line compute nodes"

    os_repodir="${TORTUGA_ROOT}/www_int/compute-os-repo"

    mkdir -p "${os_repodir}"

    createrepo "${os_repodir}" >>/tmp/install-tortuga.log 2>&1
}

donemsg="Tortuga successfully installed."

# Log installation completion including timestamp
echo "<<<<< $donemsg ($(date))" >>/tmp/install-tortuga.log

echo "${donemsg}"

echo
echo "Complete Tortuga set up as follows:"
echo
echo "${TORTUGA_ROOT}/bin/tortuga-setup"
echo

exit 0
