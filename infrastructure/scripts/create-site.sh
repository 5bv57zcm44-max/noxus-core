#!/usr/bin/env bash
set -euo pipefail
cd /home/frappe/frappe-bench

site="${NOXUS_SITE:?NOXUS_SITE is required}"
if [ -f "sites/$site/site_config.json" ]; then
  echo "Site $site already exists; applying migrations"
  bench --site "$site" migrate
  exit 0
fi

env/bin/python /opt/noxus/scripts/create_site.py
bench --site "$site" install-app noxus_core
if [ "${NOXUS_WITH_ERPNEXT:-0}" = "1" ]; then
  bench --site "$site" install-app erpnext
fi
IFS=',' read -ra apps <<< "${NOXUS_APPS:-}"
for app in "${apps[@]}"; do
  if [ -n "$app" ] && [ "$app" != "noxus_core" ]; then
    bench --site "$site" install-app "$app"
  fi
done
bench --site "$site" migrate
bench --site "$site" execute noxus_core.install.after_install
