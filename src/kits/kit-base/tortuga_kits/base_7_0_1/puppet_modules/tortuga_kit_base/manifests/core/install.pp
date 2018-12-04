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


# Not to be confused with 'installer' :)

class tortuga_kit_base::core::install::virtualenv::package {
  require tortuga_kit_base::core::install::virtualenv::pre_install

  if $facts['os']['family'] == 'RedHat' {
    if $facts['os']['name'] == 'Amazon' {
      # Amazon Linux has a native python36 package
      $pkgs = [
        'python36',
      ]
    } else {
      # python36 must be installed from SCL on RHEL and CentOS
      $pkgs = [
        'rh-python36-python-virtualenv',
      ]

      if $facts['os']['name'] == 'RedHat' {
        # enable rhscl repository on RHEL
        exec { 'enable rhscl repository':
          command => 'yum-config-manager --enable rhui-REGION-rhel-server-rhscl',
          path    => ['/bin', '/usr/bin'],
          unless  => 'yum repolist | grep -q rhscl',
        }

        Exec['enable rhscl repository']
          -> Package['rh-python36-python-virtualenv']
      } elsif $facts['os']['name'] == 'CentOS' {
        # Set up SCL repository
        ensure_packages(['centos-release-scl'], {'ensure' => 'installed'})

        # Install Python 3.6 from SCL repository
        Package['centos-release-scl']
          -> Package['rh-python36-python-virtualenv']
      }

      # Install Python 3.6 package and dependencies
      ensure_packages($pkgs, {'ensure' => 'installed'})
    }
  } elsif $facts['os']['name'] == 'Ubuntu' {

      $pkgs = [
        'python3.6',
        'python3.6-venv',
      ]
  } elsif $::osfamily == 'Debian' {
      $pkgs = [
        'python3',
        'python3-venv',
      ]
  } else {
    $pkgs = []
  }

  if $pkgs {
    ensure_packages($pkgs, {'ensure' => 'installed'})
  }
}

class tortuga_kit_base::core::install::virtualenv::pip {
  require tortuga_kit_base::core::install::virtualenv::pre_install

#   ensure_resource('package', 'virtualenv', {
#     ensure   => installed,
#     provider => 'pip',
#   })
}

# set up any repositories required to bootstrap virtualenv
class tortuga_kit_base::core::install::virtualenv::pre_install {
  require tortuga::packages

  if $facts['os']['name'] == 'Ubuntu' {
    include apt

    # install PPA containing Python 3.6
    apt::ppa { 'ppa:deadsnakes/ppa':
      ensure => present,
    }
  }
}

class tortuga_kit_base::core::install::virtualenv {
  contain tortuga_kit_base::core::install::virtualenv::pre_install

  case $::osfamily {
    'RedHat', 'Debian': { contain tortuga_kit_base::core::install::virtualenv::package }
    'Suse': { contain tortuga_kit_base::core::install::virtualenv::pip }
  }
}

class tortuga_kit_base::core::install::create_tortuga_instroot {
  require tortuga_kit_base::core::install::virtualenv

  include tortuga::config

  if $facts['os']['family'] == 'RedHat' {
    # Amazon Linux is the exception here since it puts python3 in the
    # default PATH
    $virtualenv = $facts['os']['name'] ? {
      'Amazon' => 'python3 -m venv',
      default  => '/opt/rh/rh-python36/root/bin/python -m venv',
    }
  } elsif $facts['os']['family'] == 'Debian' {
    if $facts['os']['name'] == 'Ubuntu' {
      # explicitly specify python3.6 as the Python interpreter on Ubuntu in
      # the event that 3.5 is also installed
      $virtualenv = 'python3.6 -m venv'
    } else {
      $virtualenv = 'python3 -m venv'
    }
  } else {
    $virtualenv = $::osfamily ? {
      'Suse'   => 'virtualenv --system-site-packages',
      default  => undef,
    }
  }

  if $virtualenv == undef {
    fail("virtualenv command not defined for ${::operatingsystem}")
  }

  exec { 'create_tortuga_base':
    path    => ['/bin', '/usr/bin', '/usr/local/bin'],
    cwd     => '/tmp',
    command => "${virtualenv} ${tortuga::config::instroot}",
    creates => $tortuga::config::instroot,
  }

  file { ["${tortuga::config::instroot}/var/run",
          "${tortuga::config::instroot}/var",
          "${tortuga::config::instroot}/var/tmp"]:
    ensure => directory,
    require => Exec['create_tortuga_base'],
  }
}

class tortuga_kit_base::core::install::install_tortuga_base {
  require tortuga_kit_base::core::install::create_tortuga_instroot

  include tortuga::config

  $intweburl = "http://${::primary_installer_hostname}:${tortuga::config::int_web_port}"

  $tortuga_pkg_url = "${intweburl}/python-tortuga/simple/"

  $pipcmd = "${tortuga::config::instroot}/bin/pip"

  $pip_install_opts = "--extra-index-url ${tortuga_pkg_url} \
--trusted-host ${::primary_installer_hostname}"

  exec { 'install tortuga-core Python package':
    command => "${pipcmd} install ${pip_install_opts} tortuga-core",
    unless  => "${pipcmd} show tortuga-core",
  }
}

class tortuga_kit_base::core::install::bootstrap {
  require tortuga_kit_base::core::install::install_tortuga_base

  include tortuga::config

  if $tortuga::config::proxy_uri {
    $env = [
      "https_proxy=${tortuga::config::proxy_uri}",
    ]
  } else {
    $env = undef
  }

  exec { 'generate_nii_profile':
    path        => ['/bin', '/usr/bin'],
    command     => "${tortuga::config::instroot}/bin/generate-nii-profile --installer ${::primary_installer_hostname} --node ${::fqdn}",
    environment => $env,
    unless      => 'test -f /etc/profile.nii',
  }
}

class tortuga_kit_base::core::install::final {
  require tortuga_kit_base::core::install::bootstrap

  include tortuga::config

  if $tortuga::config::proxy_uri {
    $env = [
      "https_proxy=${tortuga::config::proxy_uri}",
    ]
  } else {
    $env = undef
  }

  exec { 'update_node_status':
    path        => ['/bin', '/usr/bin'],
    command     => "${tortuga::config::instroot}/bin/update-node-status --status Installed",
    environment => $env,
    tries       => 10,
    try_sleep   => 10,
    unless      => "test -f ${tortuga::config::instroot}/var/run/CONFIGURED",
  } ~>
  exec { 'drop_configured_marker':
    path        => ['/bin', '/usr/bin'],
    command     => "touch ${tortuga::config::instroot}/var/run/CONFIGURED",
    refreshonly => true,
  }
}

class tortuga_kit_base::core::install {
  require tortuga_kit_base::core::cfmsecret
  require tortuga_kit_base::core::certificate_authority

  contain tortuga_kit_base::core::install::virtualenv
  contain tortuga_kit_base::core::install::create_tortuga_instroot
  contain tortuga_kit_base::core::install::install_tortuga_base
  contain tortuga_kit_base::core::install::bootstrap
  contain tortuga_kit_base::core::install::final
}
