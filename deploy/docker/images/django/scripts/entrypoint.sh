#!/bin/bash

set -e

CURRENT_DIR=`dirname "${BASH_SOURCE[0]}"`

# Wait for postgres db to become available
python $CURRENT_DIR/wait_for_db.py
>&2 echo 'PostgreSQL is available'

# Evaluate passed CMD
exec "$@"
