# A description of what this class does
#
# @summary A short summary of the purpose of this class
#
# @example
#   include tortuga::installer::redis::install

class tortuga::installer::redis::install {
  require tortuga::packages

  package { 'redis':
    ensure => latest
  }

}