#!/bin/bash

# This script creates a tarball containing all UniCloud third-party
# dependencies to facilitate installations where there is no
# internet access.

# set -u

readonly distmajversion=7

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

readonly dstdir="`pwd`/tortuga-deps"

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
git \
rh-python36 \
redis \
zeromq3 \
"

required_pkgs="${pkgs}"

readonly puppet_module_urls="https://forge.puppet.com/v3/files/puppetlabs-stdlib-5.2.0.tar.gz"

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
    echo -n "Checking for puppet repo... "

    rpm --query --quiet puppet5-release && {
        echo "found"
    } || {
        echo "not found"

        yum install -y "http://yum.puppetlabs.com/puppet5/puppet5-release-el-${distmajversion}.noarch.rpm"
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

    # disable 'updates' repo; this may not be the desired behaviour for some
    # installations
    local yumopts="--disablerepo=updates --downloadonly --downloaddir=${rpmdstdir}"

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

    ( cd "${rpmdstdir}"; createrepo . )
}

download_puppet_modules() {
    [[ -n ${1} ]] || return

    local puppet_dstdir=${dstdir}/puppet
    local localfile
    local curl_args

    mkdir -p "${puppet_dstdir}"

    for url in ${1}; do
        localfile="$(pwd)/$(basename "${url}")"

	[[ -f "${localfile}" ]] && curl_args="--time-cond ${localfile}"

        ( cd "${puppet_dstdir}"; curl --remote-name ${curl_args} ${url} )
    done
}

download_python_packages() {
    cat >requirements.txt <<ENDL
alabaster==0.7.12
amqp==2.3.2
asn1crypto==0.24.0
awscli==1.16.132
backports.functools-lru-cache==1.5
Beaker==1.10.0
billiard==3.5.0.4
boto==2.49.0
boto3==1.9.122
botocore==1.12.122
celery==4.2.1
certifi==2018.10.15
cffi==1.11.5
chardet==3.0.4
cheroot==6.5.2
CherryPy==18.0.1
Click==7.0
colorama==0.3.9
cryptography==2.4.1
daemonize==2.4.7
docutils==0.14
future==0.17.1
gevent==1.3.7
greenlet==0.4.15
idna==2.7
jaraco.functools==1.20
Jinja2==2.10
jmespath==0.9.4
kombu==4.2.1
Mako==1.0.7
MarkupSafe==1.1.0
marshmallow==2.16.3
marshmallow-sqlalchemy==0.15.0
more-itertools==4.3.0
oic==0.14.0
passlib==1.7.1
pip2pi @ git+https://github.com/UnivaCorporation/pip2pi.git@univa-stable#egg=pip2pi-0.8.0
pip==19.0.3
portend==2.3
pyasn1==0.4.5
pycparser==2.19
pycryptodomex==3.7.0
pyjwkest==1.4.0
pyOpenSSL==18.0.0
python-dateutil==2.7.5
python-hostlist==1.18
pytz==2018.7
PyYAML==3.13
pyzmq==17.1.0
redis==2.10.6
repoze.lru==0.7
requests==2.20.1
Routes==2.4.1
rsa==3.4.2
s3transfer==0.2.0
six==1.11.0
SQLAlchemy==1.2.14
tempora==1.14
urllib3==1.24.1
vine==1.1.4
virtualenv==15.1.0
websockets==7.0
ENDL

    # create virtualenv
    . /opt/rh/rh-python36/enable

    python3 -m venv tmp-venv

    tmp-venv/bin/pip install --upgrade pip==19.0.3
    tmp-venv/bin/pip install git+https://github.com/UnivaCorporation/pip2pi.git@univa-stable#egg=pip2pi-0.8.0

    tmp-venv/bin/pip2pi ${dstdir}/python -r requirements.txt

    tmp-venv/bin/dir2pi ${dstdir}/python
}

# create destination directory
[[ $force -eq 0 ]] && {
    [[ ! -d ${dstdir} ]] || {
        echo "Error: destination directory ${dstdir} already exists." >&2
        echo >&2
        echo "Please delete it to force redownloading of Tortuga installation \
    dependencies." >&2

        exit 1
    }
} || {
    # remove existing destination directory
    rm -rf ${dstdir}
}

[[ $quiet -eq 1 ]] || {
    rpm --query --quiet createrepo || {
        echo "This script will install the following packages on *this* host:"
        echo
        echo "  - createrepo"
        echo "  - centos-release-scl"
        echo "  - git"
        echo "  - rh-python36"
        echo

        read -p "Do you wish to continue [N/y]? " response

        [[ $(echo ${response} | tr [A-Z] [a-z] | cut -c1) != y ]] && {
            echo "Aborted by user" >&2

            exit 1
        }
    }
}

rpm --query --quiet centos-release-scl || yum install -y centos-release-scl
rpm --query --quiet git || yum install -y git

mkdir -p ${dstdir}

yum install -y rh-python36

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

echo
echo "Dependencies download complete."
echo

du -sh ${dstdir}

echo
