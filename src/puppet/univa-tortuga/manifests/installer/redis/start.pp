# A description of what this class does
#
# @summary A short summary of the purpose of this class
#
# @example
#   include tortuga::installer::redis::start

class tortuga::installer::redis::start {
  require tortuga::installer::redis::install

  $redis_config_file = '/etc/redis.conf'
  $redis_password = generate("/bin/cat ${tortuga::installer::redis::install::redis_password_file}")

  file { $redis_config_file:
    content => template('tortuga/redis.conf.tmpl'),
    mode    => '0640',
    owner   => 'redis',
    group   => 'root',
  }

  service { 'redis':
    ensure => running,
    enable => true,
    require => File[$redis_config_file]
  }

}
