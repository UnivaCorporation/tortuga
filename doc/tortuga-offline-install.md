# Tortuga Offline Installation

## Overview

This document describes the installation procedure for Tortuga 7.x on servers
that do not have internet access.

It is *assumed* that the distribution package repositories are available.

## Downloading Dependencies

The script `prep-offline-install.sh` script is intended to be run on a
connected host; one that has unrestricted access to package repositories
required by the Tortuga installer. This includes `yum.puppetlabs.com`, the EPEL
repository, and sites redirected from PyPI (the Python Package Index).

1. Run `prep-offline-install.sh` script

    Depending on bandwidth, this will take a few seconds to a few minutes.
    The total dependencies downloaded are approximately 150MB.

    The files will be downloaded to a subdirectory named `tortuga-deps`
    in the local directory.

    **Note:** some (most?) warnings/errors displayed during execution of
    `prep-offline-install.sh` can be safely ignored.

1. Create tar from artifacts

        tar czf tortuga-deps.tar.gz tortuga-deps/

1. Copy dependencies tarball

    Copy the dependencies tarball to the server where Tortuga is to be
    installed.

## Tortuga Installation

1. Extract dependencies tarball

    Extract the dependencies tarball from the previous step.

        tar zxf tortuga-deps.tar.gz -C /tmp

    This command will create the directory `/tmp/tortuga-deps`.

1. Installing Tortuga using local dependencies

    It is necessary to run run `install-tortuga.sh` with the
    `--dependencies-dir` argument, otherwise it will use the internet to
    download dependencies.

        install-tortuga.sh --dependencies-dir=/tmp/tortuga-deps

    `/opt/tortuga/bin/tortuga-setup` can be run as normal after running
    `install-tortuga.sh`.

    Provisioned compute nodes are automatically configured to use the local
    installation dependencies, instead of connecting to remote sites.
