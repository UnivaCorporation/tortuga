# A description of what this class does
#
# @summary A short summary of the purpose of this class
#
# @example
#   include tortuga::installer::redis::install

class tortuga::installer::redis::install {
  require tortuga::packages

  $redis_password_file = "${tortuga::config::etc_dir}/redis.passwd"

  ensure_packages(['redis'], {'ensure' => 'installed'})

  file { $redis_password_file:
    content => generate('/bin/openssl rand -base64 32'),
    mode    => '0600',
    owner   => 'root',
    group   => 'root',
    replace => false
  }

}
