FROM node:24.18.0-bookworm-slim@sha256:6f7b03f7c2c8e2e784dcf9295400527b9b1270fd37b7e9a7285cf83b6951452d AS node

FROM python:3.14.6-slim-bookworm@sha256:86f975aca15cf04a40b399eebede9aea7c82eae084d1f1a0a6ef6bcaae871a30 AS build

ARG FRAPPE_COMMIT=be4728af84ecdec9e3e555f0aca1a7766d3f1811
ARG ERPNEXT_COMMIT=a5de60c357d531cb31da093f0b86301776965173
ARG WITH_ERPNEXT=0

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FRAPPE_BENCH_ROOT=/home/frappe/frappe-bench \
    NODE_PATH=/opt/noxus/socketio-runtime/node_modules \
    PATH=/home/frappe/.local/bin:/home/frappe/frappe-bench/env/bin:/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin

COPY --from=node /usr/local/ /usr/local/
RUN apt-get update && apt-get install --yes --no-install-recommends \
      build-essential cron curl file git gosu jq libffi-dev libjpeg62-turbo-dev libmariadb-dev libpq-dev \
      libssl-dev mariadb-client pkg-config redis-tools wkhtmltopdf xvfb \
    && rm -rf /var/lib/apt/lists/* \
    && rm -f /usr/local/bin/yarn /usr/local/bin/yarnpkg \
    && npm install --global yarn@1.22.22 \
    && test "$(yarn --version)" = "1.22.22" \
    && useradd --create-home --shell /bin/bash frappe \
    && python -m pip install --no-cache-dir \
         frappe-bench==5.27.0 \
         msgpack==1.2.1 \
         setuptools==83.0.0

USER frappe
WORKDIR /home/frappe
RUN git clone --filter=blob:none https://github.com/frappe/frappe.git /tmp/frappe \
    && git -C /tmp/frappe checkout "$FRAPPE_COMMIT" \
    && bench init --skip-assets --skip-redis-config-generation --frappe-path /tmp/frappe --python /usr/local/bin/python frappe-bench \
    && ./frappe-bench/env/bin/python -m pip install --no-cache-dir \
         msgpack==1.2.1 \
         setuptools==83.0.0 \
    && rm -rf /home/frappe/.cache/pip \
    && rm -rf /tmp/frappe/.git

COPY --chown=frappe:frappe frappe_apps /opt/noxus/apps
COPY --chown=frappe:frappe infrastructure/scripts /opt/noxus/scripts
COPY --chown=frappe:frappe infrastructure/docker/socketio-runtime /opt/noxus/socketio-runtime
WORKDIR /home/frappe/frappe-bench
RUN set -eu; \
    printf 'frappe\n' > sites/apps.txt; \
    for app_source in /opt/noxus/apps/noxus_*; do \
      app_name="$(basename "$app_source")"; \
      cp -a "$app_source" "apps/$app_name"; \
      ./env/bin/python -m pip install --no-cache-dir --editable "apps/$app_name"; \
      printf '%s\n' "$app_name" >> sites/apps.txt; \
    done \
    && if [ "$WITH_ERPNEXT" = "1" ]; then \
         git clone --filter=blob:none https://github.com/frappe/erpnext.git /tmp/erpnext \
         && git -C /tmp/erpnext checkout "$ERPNEXT_COMMIT" \
         && rm -rf /tmp/erpnext/.git \
         && cp -a /tmp/erpnext apps/erpnext \
         && ./env/bin/python -m pip install --no-cache-dir --editable apps/erpnext \
         && yarn --cwd apps/erpnext install --frozen-lockfile --non-interactive \
         && printf 'erpnext\n' >> sites/apps.txt \
         && rm -rf /tmp/erpnext; \
       fi \
    && ./env/bin/python -m pip install --no-cache-dir \
         cryptography==48.0.1 \
         msgpack==1.2.1 \
         Pillow==12.3.0 \
         pypdf==6.14.2 \
         setuptools==83.0.0 \
    && bench build --production \
    && npm ci --prefix /opt/noxus/socketio-runtime --omit=dev --ignore-scripts --no-audit --no-fund \
    && rm -rf \
         apps/frappe/node_modules \
         apps/erpnext/node_modules \
         apps/erpnext/banking/node_modules \
         /home/frappe/.cache/pip \
         /home/frappe/.cache/yarn

USER root
RUN rm -rf \
         /usr/local/bin/npm \
         /usr/local/bin/npx \
         /usr/local/bin/yarn \
         /usr/local/bin/yarnpkg \
         /usr/local/lib/node_modules/npm \
         /usr/local/lib/node_modules/yarn

# Copy the sanitized runtime filesystem into a fresh final stage so superseded
# package metadata cannot survive in lower image layers and trigger scanners.
FROM scratch AS runtime
COPY --from=build / /

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FRAPPE_BENCH_ROOT=/home/frappe/frappe-bench \
    NODE_PATH=/opt/noxus/socketio-runtime/node_modules \
    PATH=/home/frappe/.local/bin:/home/frappe/frappe-bench/env/bin:/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin

USER frappe
WORKDIR /home/frappe/frappe-bench

EXPOSE 8000 9000
CMD ["bench", "serve", "--port", "8000"]
