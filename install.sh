#!/bin/sh
# Installs the cad-doc skill. Arguments are passed on to install.py (see there).
exec python3 "$(dirname "$0")/install.py" "$@"
