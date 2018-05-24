# A description of what this class does
#
# @summary A short summary of the purpose of this class
#
# @example
#   include tortuga::installer::redis

class tortuga::installer::redis {
  contain tortuga::installer::redis::install
  contain tortuga::installer::redis::start
}
