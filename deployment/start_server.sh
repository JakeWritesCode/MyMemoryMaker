#!/usr/bin/env bash
# start-server.sh
(cd /opt/app/MyMemoryMaker; gunicorn my_memory_maker.wsgi --worker-tmp-dir /dev/shm --user www-data --bind 0.0.0.0:8010 --workers 3) &
nginx -g "daemon off;"
chown -R celery:celery /var/run/celery
chown -R celery:celery /var/log/celery
/etc/init.d/celeryd start
/etc/init.d/celerybeat start