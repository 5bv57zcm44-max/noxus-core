#!/usr/bin/env bash
set -euo pipefail
cd /home/frappe/frappe-bench
bench set-config -g db_host mariadb
bench set-config -g db_port 3306
bench set-config -g redis_cache redis://redis-cache:6379
bench set-config -g redis_queue redis://redis-queue:6379
bench set-config -g redis_socketio redis://redis-socketio:6379
bench set-config -g socketio_port 9000
bench set-config -g serve_default_site true
