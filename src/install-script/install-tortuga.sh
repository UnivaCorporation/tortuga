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
readonly tortuga_version="7.0.1"

TEMP=$( getopt -o v,f --long force,verbose,debug,help,\
disable-package-caching,\
download-only,force-hostname -n $(basename $0) -- "$@" )

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

# expect to find 'python-tortuga' in the Tortuga distribution tarball
[[ -d python-tortuga/simple ]] || {
    echo "Error: Tortuga distribution tarball is missing files" >&2
    exit 1
}

# get expanded path to Tortuga Python packages
local_tortuga_pip_repository=$(cd python-tortuga; pwd -P)

# ensure Tortuga Python package repository is included
pip_install_opts="--extra-index-url file://${local_tortuga_pip_repository}/simple"

[[ ${DEBUG} -eq 0 ]] && pip_install_opts="${pip_install_opts} --quiet"

if [ $DEBUG -eq 1 ]; then
    YUMCMD="yum"
else
    YUMCMD="yum -e 0 -d 0 --quiet"
fi

pkgs=""

readonly basearch=`arch`

function get_distro() {
    if $(type -P rpm &>/dev/null); then
        # rpm is installed, attempt to determine version
        if `rpm --quiet -q centos-release`; then
            dist="centos"
        elif `rpm --quiet -q oraclelinux-release`; then
            dist="oracle"
        elif `rpm --quiet -q redhat-release-server`; then
            dist="rhel"
        elif `rpm --quiet -q redhat-release-workstation`; then
            dist="rhel"
        elif `rpm --quiet -q fedora-release`; then
            dist="fedora"
        else
            dist="unknown"
        fi
    else
        echo "Error: this system does not appear to be using RPM."
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
        fedora)
            relpkgname="fedora-release"
            ;;
        *)
            # Unable to determine Linux distribution
            return 1
            ;;
     esac

     # Attempt to extract the major version number
     if [ "$1" == "fedora" ]; then
         rpm -qi $relpkgname | awk '/^Version/ {print substr($3,0,2)}'
     elif [[ $1 == centos ]]; then
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

            if ! `pkgexists $relpkgname`; then
                # Check for "Workstation" installation
                relpkgname="redhat-release-workstation"
            fi
            ;;
        fedora)
            relpkgname="fedora-release"
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
    if [[ $distro_family == rhel ]] || [[ $distro_family == fedora ]]; then
        rpm --query --quiet $1
    else
        if [ $DEBUG -eq 1 ]; then
            echo "[debug] pkgexists(): unsupported distro \"${distro_family}\""
        fi

        return 0
    fi
}

function installpkg() {
    local pkg="$1"

    if `pkgexists $pkg`; then return 0; fi

    # Install the package
    $YUMCMD -y install $pkg >>/tmp/install-tortuga.log 2>&1
}

function install_epel() {
    local epelpkgname="epel-release"

    local epel_release_url="http://dl.fedoraproject.org/pub/epel/${epelpkgname}-latest-${distmajversion}.noarch.rpm"

    # Check if 'epel-release' package is already installed
    if `pkgexists $epelpkgname`; then return; fi

    echo "Installing ${epelpkgname}... " | tee -a /tmp/install-tortuga.log

    # Attempt to install 'epel-release' using default URL
    for ((i=0; i<5; i++)); do
        # Attempt to install 'epel-release'
        rpm --install --quiet ${epel_release_url} | tee -a /tmp/install-tortuga.log

        if [ $? -ne 0 ]; then continue; fi

        break
    done

    if ! `pkgexists $epelpkgname`; then
        echo "Error installing ${epelpkgname} (${epel_release_url}). Unable to proceed." | tee -a /tmp/install-tortuga.log
        exit 1
    fi
}

function check_puppet_memory() {
    local total_memory=$(free -g | grep "Mem:" | awk '{ print $2 }')

    if [ "$total_memory" -lt "2" ] && [ "$1" -lt "1" ]; then
        echo "Error: Puppet requires at least 2GB of memory" | tee -a /tmp/install-tortuga.log
        echo -e "\t ...ignore with --force"
        exit 1
    fi
}

function install_puppetlabs_repo {
    local puppetlabspkgname="puppet5-release"

    if `pkgexists $puppetlabspkgname`; then return; fi

    echo "Installing ${puppetlabspkgname}... " | tee -a /tmp/install-tortuga.log

    if [ $distro_family = "rhel" ]; then
        if [[ $distmajversion -lt 6 ]] || [[ $distmajversion -gt 7 ]]; then
            echo "Error: unsupported RHEL version (${distmajversion})" | tee -a /tmp/install-tortuga.log
            exit 1
        fi

        puppetlabs_release_url="http://yum.puppetlabs.com/puppet5/${puppetlabspkgname}-el-${distmajversion}.noarch.rpm"
    elif [ "$dist" == "fedora" ]; then
        if [[ $distmajversion -lt 19 ]] || [[ $distmajversion -gt 20 ]]; then
            echo "Error: unsupported Fedora version (${distmajversion})" | tee -a /tmp/install-tortuga.log
            exit 1
        fi
    else
        echo "Error: unsupported Linux distribution (${dist})" | tee -a /tmp/install-tortuga.log
        exit 1
    fi

    for ((i=0; i < 5; i++)); do
        rpm --install --quiet $puppetlabs_release_url 2>/dev/null | \
            tee -a /tmp/install-tortuga.log

        if [ $? -ne 0 ]; then continue; fi

        break
    done

    if ! `pkgexists $puppetlabspkgname`; then
        echo "Error installing ${puppetlabspkgname} ($puppetlabs_release_url). Unable to proceed." | tee -a /tmp/install-tortuga.log
        exit 1
    fi
}

function cachepkgs {
    if [ -z "$*" ]; then return; fi

    local inst_pkgs=""
    local reinst_pkgs=""

    for pkg in $*; do
        if ! `pkgexists $pkg`; then
            # Package is not installed
            inst_pkgs="$inst_pkgs $pkg"
        else
            # Package is installed
            reinst_pkgs="$reinst_pkgs $pkg"
        fi
    done

    local yumcmd="${YUMCMD} --downloadonly --downloaddir=${ucpkgcachedir}"

    if [ $download_only -ne 1 ]; then
        echo -n "Please wait... caching installation package dependencies... "
    else
        echo -n "Please wait... "
    fi

    if [[ -n $inst_pkgs ]]; then
        # Packages that aren't already installed on this host
        $yumcmd -y install $inst_pkgs 2>&1 >>/tmp/install-tortuga.log
    fi

    if [[ -n $reinst_pkgs ]]; then
        $yumcmd -y reinstall $reinst_pkgs 2>&1 >>/tmp/install-tortuga.log
    fi

    echo "done."

    update_pkg_cache $ucpkgcachedir
}

function update_pkg_cache {
    local cachedir="$1"

    echo "--- createrepo BEGIN ---" >>/tmp/install-tortuga.log

    createrepo $cachedir 2>&1 >>/tmp/install-tortuga.log

    echo "--- createrepo END ---" >>/tmp/install-tortuga.log
}

function installpkgs {
    if [ -z "$*" ]; then return; fi

    # Filter out list of packages that are already installed
    local tmppkg
    local pkglist=()

    for tmppkg in $*; do
        if `pkgexists $tmppkg`; then continue; fi

        pkglist[${#pkglist[*]}]=$tmppkg
    done

    if [ ${#pkglist[@]} -eq 0 ]; then return; fi

    echo "Installing packages: ${pkglist[@]}" | tee -a /tmp/install-tortuga.log

    local tmpyumcmd="${YUMCMD}"

    if [[ $enable_package_caching -eq 1 ]]; then
        # Create temporary yum.conf which includes local package cache
        cp /etc/yum.conf /tmp/yum.tortuga.conf

        cat >>/tmp/yum.tortuga.conf <<ENDL
[tortuga-local-cache]
name=tortuga-local-cache
baseurl=file://${ucpkgcachedir}
enabled=1
ENDL

        tmpyumcmd="${tmpyumcmd} -c /tmp/yum.tortuga.conf"
    fi

    local cmd="$tmpyumcmd -y install ${pkglist[@]}"

    echo "yum command: ${cmd}" >>/tmp/install-tortuga.log

    echo "--- yum BEGIN ---" >>/tmp/install-tortuga.log

    $cmd >>/tmp/install-tortuga.log 2>&1

    echo "--- yum END ---" >>/tmp/install-tortuga.log
}

function install_yum_plugins() {
    local plugin_pkgname=""

    plugin_pkgname="yum-plugin-downloadonly"

    if $(yum --help 2>&1 | grep -q "downloadonly"); then
        # Plugin is present; do not attempt to install package
        return
    fi

    if ! `pkgexists $plugin_pkgname`; then
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

if [ $FORCE -eq 1 ]; then
    intromsg="$intromsg --force argument specified."

    echo "--force argument specified on command-line" >>/tmp/install-tortuga.log
fi

# This is the first output to the console (and log file)
echo $intromsg

if [[ $download_only -ne 1 ]] && [[ -d $TORTUGA_ROOT ]] && [[ $FORCE -ne 1 ]]; then
    echo "Installation directory $TORTUGA_ROOT exists" | tee -a /tmp/install-tortuga.log
    echo
    echo "Use --force to force (re)installation"
    echo
    echo "--force not specified; exiting" >> /tmp/install-tortuga.log

    exit 1
fi

dist=`get_distro`
if [ $? -ne 0 ]; then
    exit 1
fi

distro_family=`get_distro_family $dist`
if [ $? -ne 0 ]; then
    echo "Error: unsupported distribution \"${dist}\"" | tee -a /tmp/install-tortuga.log
    exit 1
fi

# Check for RHEL major version
distmajversion=`get_dist_major_version $dist`
if [ $? -ne 0 ]; then
    echo "Error: unable to determine Linux distribution" | tee -a /tmp/install-tortuga.log
    exit 1
fi

# Get minor version
distminversion=$(get_dist_minor_version $dist)
if [ $? -ne 0 ]; then
    echo "Error: unable to determine Linux distribution" | tee -a /tmp/install-tortuga.log
    exit 1
fi

# Output debug information to the log only
echo "Detected distribution: $dist" >>/tmp/install-tortuga.log
echo "Detected distribution family: $distro_family" >>/tmp/install-tortuga.log
echo "Detected distribution major version: $distmajversion" >>/tmp/install-tortuga.log
echo "Detected distribution minor version: $distminversion" >>/tmp/install-tortuga.log

ucpkgcachedir="/tmp/tortuga_package_cache"

# Install 'createrepo', if necessary
if ! `pkgexists createrepo`; then
    installpkg createrepo
    if [ $? -ne 0 ]; then
        echo "Error installing createrepo. Check repository configuration and try again." | tee -a /tmp/install-tortuga.log
        echo "Unable to proceed!" | tee -a /tmp/install-tortuga.log
        exit 1
    fi
fi

# Create temporary package cache dir
if [[ $enable_package_caching -eq 1 ]]; then
    echo "Using temporary directory $ucpkgcachedir for package cache" >> /tmp/install-tortuga.log

    # Prepare for cache packages; without having to jump through hoops, this
    # creates the package cache directory regardless of whether caching is
    # enabled or not. This prevents having to do something funky in Puppet to
    # detect this.
    #
    # TODO: use Hiera to store package cache setting

    if [[ $FORCE -eq 1 ]]; then
        echo "Removing directory \"${ucpkgcachedir}\"" | tee -a /tmp/install-tortuga.log

        rm -rf $ucpkgcachedir
    fi

    [[ -d $ucpkgcachedir ]] || mkdir -p $ucpkgcachedir

    # Initialize the newly created (empty) directory as a valid repository
    update_pkg_cache $ucpkgcachedir
fi

# Apply any patches needed for specific distribution
disto_patches $dist

# Check for SELinux
if $(type -P getenforce >/dev/null 2>&1); then
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
if [[ $distro_family == rhel ]] || [[ $distro_family == fedora ]]; then
    install_yum_plugins
fi

# Check for curl
if ! `type -P curl >/dev/null 2>&1`; then
    echo "Installing curl..."
    installpkg curl
    if [ $? -ne 0 ]; then
        echo "Error installing curl. Check repository configuration and try again" | tee -a /tmp/install-tortuga.log
        echo "Unable to proceed!" | tee -a /tmp/install-tortuga.log
        exit 1
    fi
fi

# Check if 'epel-release' is installed, if not install it.
# NOTE: epel-release gets installed regardless, as it is a required source
# for dependent packages, not just puppet.
if [[ $distro_family == rhel ]]; then
    install_epel
fi

# Check there's enough memory for Puppet
check_puppet_memory $FORCE

# Install puppetlabs repo
install_puppetlabs_repo

# Check for puppet binary in system path
if ! `type -P puppet >/dev/null 2>&1`; then
    # Install 'puppet-agent' indepdendently of the other packages
    # in order to properly warn of possible missing dependent packages.
    pkgs="puppet-agent"

    installpkgs $pkgs

    # yum doesn't return a useful return code in the case of error, so we
    # validate the packages manually.
    for pkg in $pkgs; do
        if ! `pkgexists $pkg`; then
            echo "Error installing package \"${pkg}\"." | tee -a /tmp/install-tortuga.log
            echo

            if [[ $dist == rhel ]]; then
                echo "Ensure \"optional\" RPMs channel is enabled, otherwise" \
                    "check network and/or Yum repository configuration." \
                    | fold -sw $wrapwidth | tee -a /tmp/install-tortuga.log
            else
                echo "Check network and/or Yum repository configuration" \
                     " and restart" | tee -a /tmp/install-tortuga.log
            fi

            exit 1
        fi
    done

fi

# 'pkgs' is a list of packages to be installed on the Tortuga installer
# 'cachedpkgs' are cached for use by on-prem nodes

if [[ $distro_family == rhel ]]; then
    # Packages common to all RHEL versions
    pkgs="\
puppetserver \
rsync \
rh-python36 \
"

    # Packages cached for all RHEL versions
    cachedpkgs="\
puppet-agent \
"
fi

[[ ${dist} == centos ]] && {
    echo "Installing SCL repository... "
    installpkg centos-release-scl
    [[ $? -eq 0 ]] || {
        echo "Error installing \"centos-release-scl\". Unable to proceed." >&2
        exit 1
    }
}

if [ $enable_package_caching -eq 1 ]; then
    cachepkgs $cachedpkgs
else
    echo "* Package dependency caching disabled by command-line option"
fi

# Create Tortuga internal webroot
INTWEBROOT="${TORTUGA_ROOT}/www_int"

[[ -d $INTWEBROOT/3rdparty ]] || mkdir -p "$INTWEBROOT/3rdparty"

# Download mcollective-puppet-agent plugin
echo -n "Downloading 'mcollective-puppet-agent' plugin... "

[[ -d ${INTWEBROOT}/3rdparty/mcollective-puppet-agent ]] || \
    mkdir -p ${INTWEBROOT}/3rdparty/mcollective-puppet-agent

( cd ${INTWEBROOT}/3rdparty/mcollective-puppet-agent; \
    curl --retry 10 --retry-max-time 60 --silent --fail --location --remote-name https://github.com/puppetlabs/mcollective-puppet-agent/archive/1.13.1.tar.gz 2>&1 | tee -a /tmp/install-tortuga.log )

[[ $? -eq 0 ]] || {
    echo "Error retrieving mcollective-puppet-agent. Unable to proceed" >&2
    exit 1
}

echo "done."

if [ $download_only -eq 1 ]; then
    # Force next Puppet run to synchronize newly downloaded packages
    echo "Done."

    exit 0
fi

installpkgs $pkgs

echo "Installing Tortuga Puppet integration module..." | tee -a /tmp/install-tortuga.log
/opt/puppetlabs/bin/puppet module install univa-tortuga-*.tar.gz

if [ $? -ne 0 ]; then
    echo "Installation failed... unable to proceed" | tee -a /tmp/install-tortuga.log
    exit 1
fi

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

# Install Tortuga Python packages
for module in tortuga-core tortuga-installer; do
    echo -n "Installing ${module} Python package... " | \
        tee -a /tmp/install-tortuga.log

    ${pip_install_cmd} ${module} 2>&1 >>/tmp/install-tortuga.log
    [[ $? -eq 0 ]] || {
        echo "failed."

        echo

        echo "Check /tmp/install-tortuga.log for errors" >&2

        exit 1
    }

    echo "done."
done

# copy Tortuga Python package repository
rsync -av ${local_tortuga_pip_repository}/ ${INTWEBROOT}/python-tortuga \
    2>&1 >>/tmp/install-tortuga.log
[[ $? -eq 0 ]] || {
    echo "Error copying from \"python-tortuga\" to \"${INTWEBROOT}/python-tortuga\"" >&2

    echo >&2

    echo "Installation failed." >&2

    exit 1
}

# Create required directories
for dirname in var/lib var/action-log; do
    [[ -d $TORTUGA_ROOT/$dirname ]] || mkdir -p "$TORTUGA_ROOT/$dirname"
done

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

for filename in $(find . -maxdepth 1 -type f -name 'kit-*.tar.bz2'); do
    echo -n "   $(basename ${filename})... "
    cp -f "${filename}" "${kitsdir}"
    echo "done."
done

if [[ $enable_package_caching -eq 1 ]]; then
    # Copy cached packages from temporary directory to proper location
    echo -n "Synchronizing cached packages for use by compute nodes... " | tee -a /tmp/install-tortuga.log

    dstdir=$TORTUGA_ROOT/repos/3rdparty/$distro_family/$distmajversion/$basearch

    mkdir -p "${dstdir}"

    # We only want the output from this rsync to appear in the log file, not
    # on the console.
    rsync -av $ucpkgcachedir/ $dstdir/ 2>&1 >>/tmp/install-tortuga.log

    [[ $? -ne 0 ]] && {
        echo " failed."
        echo
        echo "Error copying cached packages; check free disk space"

        exit 1
    } | tee -a /tmp/install-tortuga.log

    echo "done." | tee -a /tmp/install-tortuga.log
fi

donemsg="Tortuga successfully installed."

# Log installation completion including timestamp
echo "<<<<< $donemsg ($(date))" >>/tmp/install-tortuga.log

echo $donemsg

echo
echo "Complete Tortuga set up as follows:"
echo
echo "${TORTUGA_ROOT}/bin/tortuga-setup"
echo

exit 0
