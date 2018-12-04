#!/bin/bash

# This script creates a tarball containing all UniCloud third-party
# dependencies to facilitate installations where there is no
# internet access.

set -u

force=0
quiet=0

TEMP=$(getopt -o q --long quiet,force -- "$@")
[[ $? -eq 0 ]] || {
    echo "Terminating..." >&2
    exit 1
}

eval set -- "${TEMP}"

while true; do
    case "${1}" in
        -q|--quiet)
            quiet=1
            shift
            ;;
        --force)
            force=1
            shift
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "Internal error!" >&2
            exit 1
            ;;
    esac
done

readonly dstdir="`pwd`/unicloud-deps"

# detect distribution
distver=$(rpm --query centos-release --queryformat "%{VERSION}")
[[ $? -eq 0 ]] || {
    # check for RHEL
    distver=$(rpm --query redhat-release-server --queryformat "%{VERSION}" | cut -c1)
    [[ $? -eq 0 ]] || {
        echo "Error: unable to determine distribution version" >&2
        exit 1
    }
}

# master package list
readonly pkgs="puppet-agent \
puppetserver \
puppet-agent \
python-deltarpm \
PyYAML \
libyaml \
python-cheetah \
python-virtualenv \
python-ipaddr \
activemq \
zeromq3 \
python-zmq \
openpgm \
"

# TODO: currently unused
readonly distropkgs="\
which \
openssh-clients \
diffutils \
rsync \
unzip \
patch \
python-jinja2 \
MySQL-python \
sysvinit-tools \
nfs-utils \
tcpdump \
syslinux \
xinetd \
tftp-server \
bind \
dnsmasq \
pdsh \
pdsh-rcmd-ssh \
ntp \
openssh-server \
dhcp \
yum-utils \
java-1.8.0-openjdk \
openssl \
httpd \
mod_ssl \
createrepo \
python-markdown \
java-1.8.0-openjdk-headless \
python-setuptools \
net-tools \
python-markupsafe \
python-devel \
python-pygments \
python-babel \
jpackage-utils \
python-backports-ssl_match_hostname \
python-backports
tzdata-java \
copy-jdk-configs \
nss \
libjpeg-turbo \
nspr \
lksctp-tools \
nss-util \
javapackages-tools \
python-ipaddress \
nss-softokn \
libxslt \
python-javapackages \
python-pillow \
nss-softokn-freebl \
nss-sysinit \
libtiff \
python-lxml \
nss-tools \
libwebp \
jbigkit-libs \
fontconfig \

"

readonly rhel6_pkgs="python-sqlalchemy0.8"

readonly rhel7_pkgs="python-sqlalchemy"

[[ ${distver} -eq 6 ]] && {
    required_pkgs="${pkgs} ${rhel6_pkgs}"
} || {
    required_pkgs="${pkgs} ${rhel7_pkgs}"
}

readonly puppet_module_urls="https://forge.puppet.com/v3/files/puppetlabs-stdlib-4.25.1.tar.gz"

install_epel_repository() {
    local epel_repo_url=http://dl.fedoraproject.org/pub/epel/epel-release-latest-${distver}.noarch.rpm

    echo -n "Checking for EPEL repo... "

    rpm --query --quiet epel-release && {
        echo "found"
    } || {
        echo "not found"

        yum install --assumeyes ${epel_repo_url}
        retval=$?

        echo "yum returned: ${retval}"
    }
}

download_rpms() {
    local _pkgs=$@

    install_epel_repository

    local rpmdstdir="${dstdir}/rpms"

    mkdir -p ${rpmdstdir}

    # install puppetlabs repo
    echo -n "Checking for puppetlabs pc1 repo... "

    rpm --query --quiet puppetlabs-release-pc1 && {
        echo "found"
    } || {
        echo "not found"

        yum install -y http://yum.puppetlabs.com/puppetlabs-release-pc1-el-${distver}.noarch.rpm
        retval=$?

        echo "yum returned: ${retval}"
    }

    # install legacy 'puppetlabs-release' repo
    echo -n "Checking for puppetlabs-release... "
    rpm --query --quiet puppetlabs-release && {
        echo "found"
    } || {
        echo "not found"

        yum install -y http://yum.puppetlabs.com/puppetlabs-release-el-${distver}.noarch.rpm
        retval=$?

        echo "yum returned: ${retval}"
    }

    echo "Downloading packages..."

    local yumopts="--downloadonly --downloaddir=${rpmdstdir}"

    [[ -n "${_pkgs}" ]] && {
        tmpdir=$(mktemp -d)

        rpmdb --initdb --root="${tmpdir}"

        mkdir -p "${tmpdir}/etc/yum.repos.d"

        rsync -av /etc/{yum.conf,yum.repos.d} "${tmpdir}/etc"

        yum install ${yumopts} --releasever=7 --installroot="${tmpdir}" --assumeyes ${_pkgs}

        echo "Cleaning up temporary package directory"
        rm -rf "${tmpdir}"
    }

    echo "Creating Yum repository"

    ( cd ${rpmdstdir}; createrepo . )
}

download_puppet_modules() {
    [[ -n ${1} ]] || return

    local puppet_dstdir=${dstdir}/puppet

    mkdir -p ${puppet_dstdir}

    cd ${puppet_dstdir}
    for url in ${1}; do
        ( cd ${puppet_dstdir}; curl --time-cond `pwd`/$(basename ${url}) -LO ${url} )
    done

    cd ../..
}

download_python_packages() {
    local pip2pi=$(type -P pip2pi)

    [[ $? -eq 0 ]] && [[ -n $pip2pi ]] || {
        # check for local venv
        [[ -d tmpvenv ]] && [[ -x tmpvenv/bin/pip2pi ]] || {
            yum install -y python-virtualenv

            rpm --query --quiet python-virtualenv || {
                echo "Error: unable to install python-virtualenv" >&2

                exit 1
            }

            virtualenv --system-site-packages tmpvenv
            [[ $? -eq 0 ]] || {
                echo "Error creating virtualenv" >&2

                exit 1
            }
        }

        tmpvenv/bin/pip install pip2pi

        pip2pi=tmpvenv/bin/pip2pi
    }

    cat >requirements.txt <<ENDL
ipaddr
Cheetah
CherryPy<16.0
Routes
six
argparse
daemonize
boto
boto3
gevent
awscli
ENDL

    ${pip2pi} ${dstdir}/python -r requirements.txt
}

# create destination directory
[[ $force -eq 0 ]] && {
    [[ ! -d ${dstdir} ]] || {
        echo "Error: destination directory ${dstdir} already exists." >&2
        echo >&2
        echo "Please delete it to force redownloading of UniCloud installation \
    dependencies." >&2

        exit 1
    }
} || {
    # remove existing destination directory
    rm -rf ${dstdir}
}

[[ $quiet -eq 1 ]] || {
    echo "This script will install the following packages on *this* host:"
    echo
    echo "  - createrepo"
    echo "  - python-virtualenv (and dependencies)"
    echo

    read -p "Do you wish to continue [N/y]? " response

    [[ $(echo ${response} | tr [A-Z] [a-z] | cut -c1) != y ]] && {
        echo "Aborted by user" >&2

        exit 1
    }
}

mkdir -p ${dstdir}

# check for createrepo
rpm --query --quiet createrepo || {
    yum install -y createrepo

    rpm --query --quiet createrepo || {
        echo "Error installing 'createrepo'. Unable to proceed" >&2

        exit 1
    }
}

download_rpms ${required_pkgs}

download_puppet_modules ${puppet_module_urls}

download_python_packages

# other packages
mkdir -p ${dstdir}/other
( cd ${dstdir}/other; curl -s -LO https://github.com/puppetlabs/mcollective-puppet-agent/archive/1.11.1.tar.gz )

echo
echo "Dependencies download complete."
echo

du -sh ${dstdir}

echo
