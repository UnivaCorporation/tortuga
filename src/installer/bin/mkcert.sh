#!/bin/bash

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


ARGS=$(getopt -o h,v -l "help,verbose,host-name:,ip:,destdir:,server" -n "$0" -- "$@")

if [ $? -ne 0 ]; then
    echo "Internal error: terminating..." >&2
    exit 1
fi

eval set -- "$ARGS"

function usage() {
  echo "usage: $(basename $0) [--verbose|-v] [--host-name=XXXX] [--ip=XXXX] <name>"
  exit 0
}

server=0

while true; do
    case $1 in
        -v|--verbose)
            verbose=1
            shift
            ;;
        -h|--help)
            usage
            shift
            ;;
        --host-name)
            option_host_name=$2
            shift 2
            ;;
        --ip)
            option_ip=$2
            shift 2
            ;;
        --destdir)
            destdir=$2
            shift 2
            ;;
        --server)
            server=1
            shift
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "Internal error: unable to proceed!" >&2
            exit 1
            ;;
    esac
done

certname=$1

ca_dir=$TORTUGA_ROOT/etc/CA

hostdir=${destdir:-$TORTUGA_ROOT/etc/certs/$certname}

# If either CA key or CA certificate missing, attempt to recreate CA
if [[ ! -d $ca_dir ]] || [[ ! -f $ca_dir/ca-key.pem ]] || \
    [[ ! -f $ca_dir/ca.pem ]]; then
  # Ensure destination directory exists
  [[ -d $ca_dir ]] || mkdir -p $ca_dir

  # Create private key for CA
  openssl genrsa -out $ca_dir/ca-key.pem 2048

  # Initialize CA
  openssl req -x509 -new -nodes -key $ca_dir/ca-key.pem -days 3650 \
      -out $ca_dir/ca.pem -subj "/CN=tortuga-ca"
fi

# Create host directory if it doesn't already exist
[[ -d $hostdir ]] || mkdir $hostdir

sslcnf=$hostdir/${certname}-openssl.cnf

# Generate host-specific openssl.cnf
cat >$sslcnf <<ENDL
[req]
req_extensions = v3_req
distinguished_name = req_distinguished_name

[req_distinguished_name]

[ v3_req ]
ENDL

if [[ $server -eq 0 ]]; then
    # Create 'regular' (non-server) certificate

    cat >>$sslcnf <<ENDL
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
ENDL

else
    # Create 'server' certificate

    cat >>$sslcnf <<ENDL
nsCertType                     = server
# nsComment                      = "Easy-RSA Generated Server Certificate"
# subjectKeyIdentifier=hash
# authorityKeyIdentifier=keyid,issuer:always
extendedKeyUsage=serverAuth
keyUsage = digitalSignature, keyEncipherment
ENDL
fi

if [[ -n $option_host_name ]]; then
    cat >>$sslcnf <<ENDL
subjectAltName = @alt_names

[alt_names]
ENDL

    hostnames=(${option_host_name//,/ })

    for ((index=0; index < ${#hostnames[@]}; index++)); do
        echo "DNS.$(($index + 1)) = ${hostnames[$index]}" >> $sslcnf
    done
fi

if [[ -n $option_ip ]]; then
    items=(${option_ip//,/ })

    for ((index=0; index < ${#items[@]}; index++)); do
        echo "IP.$(($index + 1)) = ${items[$index]}" >> $sslcnf
    done
fi

keyfile=${certname}.key

# Generate key
openssl genrsa -out $hostdir/${keyfile} 2048

# Create certificate request
openssl req -new -key $hostdir/${keyfile} \
    -out $hostdir/${certname}.csr -subj "/CN=${certname}" \
    -config $sslcnf

# Sign the certificate
openssl x509 -req -in $hostdir/${certname}.csr -CA $ca_dir/ca.pem \
    -CAkey $ca_dir/ca-key.pem -CAcreateserial \
    -out $hostdir/${certname}.crt -days 3650 \
    -extensions v3_req -extfile $sslcnf

chmod 0400 $hostdir/$keyfile
