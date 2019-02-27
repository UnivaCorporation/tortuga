#!/bin/bash

# install 'pandoc' from pandoc.org on Ubuntu Xenial as follows:
#
#   $ curl -LO https://github.com/jgm/pandoc/releases/download/2.6/pandoc-2.6-1-amd64.deb
#   $ sudo dpkg -i pandoc-2.6-1-amd64.deb
#   $ sudo apt install -y texlive-xetex texlive-fonts-extra

# the distribution docs were built on pandoc 2.6

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# generate Github formatted doc
cat "${DIR}/header.md" "${DIR}/tortuga-7-admin-guide.md.raw" | \
    sed "/\\\\newpage/d" | pandoc -f markdown+smart \
    -o "${DIR}/tortuga-7-admin-guide.md"

# generate PDF
pandoc -f markdown+smart -H "${DIR}/listings-setup.tex" --listings \
    -o "${DIR}/tortuga-7-admin-guide.pdf" \
    --pdf-engine xelatex \
    --table-of-contents \
    --variable geometry:margin=0.5in \
    "${DIR}/tortuga-7-admin-guide.md.raw" \
    "${DIR}/metadata.yaml"
