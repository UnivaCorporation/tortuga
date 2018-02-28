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

cd "$1"
CPIO_ITEMS=`find . | wc -l`
#echo $CPIO_ITEMS
CPIO_MOD=$(( $CPIO_ITEMS / 10 ))
if [ $CPIO_MOD -eq 0 ]; then
    CPIO_MOD=$CPIO_ITEMS
fi

#echo $CPIO_MOD
find . | cpio -mpduv "$2" 2>&1| awk "
BEGIN { i=0; percent=0 }
{
   if (i % $CPIO_MOD == 0 && percent < 100) {
        printf \"%d%%.. \",percent;
        fflush(STDOUT);
        percent = percent + 10;
    }
    i=i+1;
}
END {if (percent > 0) printf \"100%%\n\"; else printf \"\n\" }"

exit $?
