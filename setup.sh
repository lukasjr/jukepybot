#!/bin/bash

: "${PORT:=5000}"
: "${HOST:="0.0.0.0"}"
flask_dir="/app/instance/vidya.sqlite"

if [ ! -e "${flask_dir}" ]; then
    flask init-db
fi

exec flask run -h "${HOST}" -p "${PORT}"
