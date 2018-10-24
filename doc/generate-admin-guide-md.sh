#!/bin/bash

set -x

type -P pandoc &>/dev/null || {
    echo "Error: this script requires pandoc" 2>&1
    exit 1
}

pandoc \
    -t gfm \
    --self-contained \
    tortuga-7-admin-guide.md.raw | \
sed "s/^\\\\newpage//" | cat doc-header.md - > tortuga-7-admin-guide.md
