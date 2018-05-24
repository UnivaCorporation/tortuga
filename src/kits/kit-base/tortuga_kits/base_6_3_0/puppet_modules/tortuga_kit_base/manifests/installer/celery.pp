# Copyright 2008-2018 Univa Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# A description of what this class does
#
# @summary A short summary of the purpose of this class
#
# @example
#   include tortuga_kit_base::installer::celery

class tortuga_kit_base::installer::celery {
  require tortuga::installer::redis

  file { '/var/log/celery':
    ensure => directory,
    owner  => root,
    group  => root,
  }

  file { '/var/run/celery':
    ensure => directory,
    owner  => root,
    group  => root,
  }

  service { 'celery':
    ensure    => running,
    enable    => true,
    require   => File['/var/log/celery']
  }
}
