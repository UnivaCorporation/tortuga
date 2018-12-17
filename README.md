# ![Tortuga](http://www.univa.com/img/tortuga_icon-rgb.png?utm_source=Tortuga%20GitHub&utm_medium=Img&utm_campaign=Tortuga%20on%20GitHub&utm_content=Tortuga%20GitHub) Tortuga - Cloud & Hybrid Clusters Made Easy

[![Build Status](https://travis-ci.org/UnivaCorporation/tortuga.svg?branch=master)](https://travis-ci.org/UnivaCorporation/tortuga)

## Tortuga Slack Channel

[Join the discussion on Slack!](https://join.slack.com/t/tortugaproject/shared_invite/enQtMzM1MDU3ODk0MjI2LThjYTNkNzFiMDc1NzdjYmJhMGZhZGI5ZDIzMzUwODBkNzU3ZDBmMGY3NzE3ZmVlNDVhMmRiY2UxNGVjZmFiNzk)

## Overview

Tortuga allows you to create and resize High Performance Computing clusters on
demand and it supports so called 'cloud bursting' in hybrid cloud scenarios.
Tortuga is tightly integrated with [Univa Grid Engine](http://www.univa.com/products/) to deliver ready-to-use clusters
including workload and resource management.

Tortuga supports so called "kits" that augment the set of software Tortuga can install as well as
the target infrastructures onto which Tortuga can deploy. Kits are installable
packages with metadata. Open source kits for Tortuga can be found under <https://github.com/UnivaCorporation/tortuga-kit-*>. The Univa Grid Engine integration is implemented as a
kit as well. The "cloud resource adapters" are also kits and Tortuga
currently supports the following cloud/virtualization platforms:

* Amazon AWS (<https://github.com/UnivaCorporation/tortuga-kit-awsadapter>)
* Google Cloud Platform (<https://github.com/UnivaCorporation/tortuga-kit-gceadapter>)
* Microsoft Azure (<https://github.com/UnivaCorporation/tortuga-kit-azureadapter>)
* Oracle Cloud Infrastructure (<https://github.com/UnivaCorporation/tortuga-kit-oraclecloudadapter>)
* OpenStack (<https://github.com/UnivaCorporation/tortuga-kit-openstackadapter>)
* VMware vSphere 5.x (<https://github.com/UnivaCorporation/tortuga-kit-vmwareadapter>)
* On-premise (physical) nodes (built-in)

Key features of Tortuga are:

* Multi-cloud support: a cluster can consist of resources from any cloud and
  resources from multiple clouds can even be used in a single cluster at the
  same time
* Reusable, interoperable components: configuration specifics for hardware and
  software get embedded in template-based profiles that can be reused and
  combined
* Automated configuration: cluster nodes are deployed to specification by
  leveraging Puppet for configuration management and deployment orchestration
* Cloud on-demand: Scaling up and down of cloud-based infrastructures happens
  dynamically dependent on workload demand and through use of a flexible rules
  engine that captures the specifics of cloud use cases
* Compatible with standard services: Tortuga integrates with and can configure
  standard services such as networking, VPNs, name resolution, identity
  management, cloud storage, and security

For a developer level introduction with instructions on how to build Tortuga
please refer to [Developer information](#developer-information).

To try Tortuga with Univa Grid Engine, you will need the [Univa Grid Engine Trial Kit](http://www.univa.com/resources/univa-navops-launch-trial-kits.php) which
can be downloaded and used for free. Installation instructions for the Univa Grid Engine Kit are available [here](https://github.com/UnivaCorporation/tortuga-kit-uge/blob/master/doc/tortuga-kit-uge.md). You should refer to the Tortuga [documentation](#documentation) in addition.

If you are interested in using Tortuga in production and you require support or
add-ons then [Univa](http://univa.com) is providing a productized version of
Tortuga under the name [Navops Launch](http://univa.com/products) together with
support options, services and integrated products.

## Documentation

The Tortuga Installation and Administration Guide (in Markdown format) is
available in the [doc](doc) subdirectory.

See the [Building documentation](#building-documentation) section below for
instructions on creating a PDF file.

### Building documentation

Tortuga documentation is provided in Markdown format which can be easily
converted to PDF using [Pandoc](https://pandoc.org).

On RHEL/CentOS 7, `pandoc` can be installed as follows:

```shell
yum install pandoc texlive-xetex texlive-collection-xetex \
    texlive-collection-latexrecommended
```

After installing `pandoc` and XeLaTeX packages, the PDF file can be generated
as follows:

```shell
pandoc -f markdown+smart \
    -o doc/tortuga-7-admin-guide.pdf \
    --pdf-engine xelatex \
    --table-of-contents \
    --variable geometry:margin=0.5in \
    doc/tortuga-7-admin-guide.md.raw \
    doc/metadata.yaml
```

To (re)generate the GitHub-formatted Markdown document, use the following:

```shell
pandoc -f markdown+smart \
    -o doc/tortuga-7-admin-guide.md \
    -t gfm \
    doc/header.md \
    doc/tortuga-7-admin-guide.md.raw
```

## Developer information

### Prerequisites

Tortuga runs on Red Hat Enterprise Linux (RHEL) or CentOS version 6 or 7 (7 is
preferred). Installation packages for it can be built on most Linux modern
distributions or macOS.

#### Python 3

Python 3.6 or higher is required and can be installed from [The Software Collections
(SCL) repository](https://wiki.centos.org/AdditionalResources/Repositories/SCL).

##### Enable SCL repository on CentOS

```shell
yum install centos-release-scl
```

##### Enable SCL repository on RHEL

On Red Hat Enterprise Linux (RHEL), the `rh-python36` package is made available
through the RHSCL channel:

```shell
yum-config-manager --enable rhel-server-rhscl-7-rpms
```

Use the following `yum-config-manager` invocation if running the official RHEL
AMI on AWS:

```shell
yum-config-manager --enable rhui-REGION-rhel-server-rhscl
```

##### Install Python 3

After installing the SCL package repository, run the following command to install Python 3.

```shell
yum install rh-python36
```

After installing `rh-python36`, source the environment to add `python3` to the system `PATH`:

```shell
. /opt/rh/rh-python36/enable
```

#### Puppet

[Puppet 5.x](https://puppet.com) is also required to build the Puppet modules used by
Tortuga. It can be installed on RHEL/CentOS by installing the distribution
version specific YUM repository package `puppet5-release` from
[http://yum.puppetlabs.com/puppet5](http://yum.puppetlabs.com/puppet5/) and
then installing the `puppet-agent` package.

Installing `puppet5-release` on RHEL/CentOS 7:

```shell
rpm -ivh http://yum.puppetlabs.com/puppet5/puppet5-release-el-7.noarch.rpm
yum install -y puppet-agent
```

This installs the Puppet suite of packages under `/opt/puppetlabs`.

Puppet 5 is also available on [Homebrew](https://brew.sh) for macOS users as `puppet-agent` cask or it is downloadable directly from [Puppet](https://puppet.com).

Independent of the method of installation, be sure you add `/opt/puppetlabs/bin` to your binary search path in `$PATH`, e.g. via reloading the shell by running `exec -l $SHELL`.

### Build instructions

Assuming the Python 3.x environment has been sourced, run the following to
build the base Tortuga installation:

    git clone git@github.com:UnivaCorporation/tortuga.git
    cd tortuga
    python3 -m venv venv
    . venv/bin/activate
    pip install -r requirements.txt
    paver build

The resultant distribution tarball can be found in the `dist` folder. Refer to
the Tortuga Installation and Administration Guide (found in the [doc](doc) folder in
this source repository) for guidance on how to install and configure Tortuga.
