# A description of what this class does
#
# @summary A short summary of the purpose of this class
#
# @example
#   include tortuga::installer::redis::start

class tortuga::installer::redis::start {
  require tortuga::installer::redis::install

  service { 'redis':
    ensure => running,
    enable => true,
  }

}
