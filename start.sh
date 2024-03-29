#!/usr/bin/env bash

wait-for-it -s "$DB_HOST:5432" -t 60
wait-for-it $RABBIT_HOST:$RABBIT_PORT -t 120

alembic -c /etc/src/alembic.ini upgrade head

gunicorn src.app:application --preload --config src/core/gunicorn.py