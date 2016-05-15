#!/bin/bash

gunicorn --worker-class eventlet -w 4 -u www-data -g www-data -p /var/run/gunicorn-dev.pid -b 0.0.0.0:80 --access-logfile /var/log/gunicorn/dev/access.log --error-logfile /var/log/gunicorn/dev/error.log --chdir /srv/wwwdev --reload app:app
