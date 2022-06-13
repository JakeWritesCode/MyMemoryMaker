#!/usr/bin/env bash
# start-server.sh

mkdir -p /var/run/celery
mkdir -p /var/log/celery
chown celery:celery /var/log/celery
chown celery:celery /var/run/celery
chmod g+w /var/run/celery
chmod g+w /var/log/celery
/etc/init.d/celeryd start
/etc/init.d/celerybeat start

(cd /opt/app/MyMemoryMaker; gunicorn my_memory_maker.wsgi --worker-tmp-dir /dev/shm --user www-data --bind 0.0.0.0:8010 --workers 3) &
nginx -g "daemon off;"
