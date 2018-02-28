#!/bin/sh

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


action="$1"

usage() {
    echo ""
    echo "usage: $0 <action> [<arguments>] <nodes>"
    echo ""
    echo "   <action> is one of:"
    echo "       add - called when node(s) are added"
    echo "       delete - called when node(s) are deleted"
    echo "       start - called when node(s) are started"
    echo "       shutdown - called when node(s) are shut down/stopped"
    echo "       reset - called when node(s) are reset"
    echo ""
    echo "   Both 'shutdown' and 'reset' actions require one argument:"
    echo "       hard - OS need not be shut down gracefully"
    echo "       soft - OS should be shut down gracefully"
    echo ""
    echo "   <nodes> is a comma-separated list of nodes"    
    exit 1
}

if [ -z "${action}" ]; then
    usage
fi
shift

check_args() {
    if [ $# -eq 0 ]; then
        echo "missing node list"
        usage
    fi
    if [ $# -gt 1 ]; then
        echo "too many arguments"
        usage
    fi
}

defaction() {
    echo "`date` $action $@" >>/tmp/bootop.log
}

multi_ssh() {
    # Perform command on (possibly) multiple targets

    # Convert targets to an array, split by commas
    local _target="$1"

    # Detemine if pdsh is available
    local _use_pdsh=$(which pdsh 2> /dev/null)

    if [ -z "${_use_pdsh}" ]; then
        # pdsh not available, so loop through every target in array

        local _target_array=( ${_target//,/ } )

        for t in "${_target_array[@]}"
        do
            # Run ssh in batch mode to prevent prompt for password
            ssh -o BatchMode=yes "$t" "$2"
        done
    else
        # Can use pdsh, do this in parallel
        pdsh -S -b -w - "$2" <<<$_target
    fi
}

do_add() {
    # do_add <nodes>
    check_args "$@"

    defaction "nodes=$@"

    # Usually a no-op
}

do_delete() {
    # do_delete <nodes>
    check_args "$@"

    defaction "nodes=$@"

    # This is probably a no-op for all installations
}

do_start() {
    # do_start <nodes>
    check_args "$@"

    defaction "nodes=$@"

    # TODO: issue power operation (IPMI, managed AC power, etc) to power on
}

do_shutdown() {
    # do_shutdown <hard|soft> <nodes>
    local _type="$1"
    shift

    check_args "$@"

    defaction "type=${_type} nodes=$@"

    # Should do poweroff command for soft shutdown, hard poweroff for hard shutdown
    multi_ssh "$@" /sbin/poweroff
}

do_reset() {
    # do_reset <hard|soft> <nodes>
    local _type="$1"
    shift

    check_args "$@"

    defaction "type=${_type} nodes=$@"

    # Should do reboot for soft reset, hard reset otherwise
    multi_ssh "$@" /sbin/reboot
}

case "${action}" in
    "add")
        do_add "$@"
        ;;
    "delete")
        do_delete "$@"
        ;;
    "start")
        do_start "$@"
        ;;
    "shutdown")
        do_shutdown "$@"
        ;;
    "reset")
        do_reset "$@"
        ;;
esac
