#!/bin/bash

set -x

systemctl stop tortugawsd

pip install -I --force-reinstall tortuga_core-7.0.0-py3-none-any.whl tortuga_installer-7.0.0-none-any.whl

( cd /opt/tortuga/alembic; alembic upgrade head )

# ensure correct permissions on database
chmod 0600 /opt/tortuga/etc/tortugadb.sqlite

systemctl start tortugawsd
