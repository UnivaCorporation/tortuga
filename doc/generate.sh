#!/bin/bash

# generate Github formatted doc
cat doc/header.md doc/tortuga-7-admin-guide.md.raw | \
    sed "/\\\\newpage/d" | pandoc -f markdown+smart \
    -o doc/tortuga-7-admin-guide.md

# generate PDF
pandoc -f markdown+smart -H listings-setup.tex --listings \
    -o doc/tortuga-7-admin-guide.pdf \
    --pdf-engine xelatex \
    --table-of-contents \
    --variable geometry:margin=0.5in \
    doc/tortuga-7-admin-guide.md.raw \
    doc/metadata.yaml
