#!/bin/bash

: "${PORT:=5000}"
flask_dir="/app/instance/vidya.sqlite"

if [ ! -e "${flask_dir}" ]; then
    flask init-db
fi

exec flask run -p "${PORT}"
