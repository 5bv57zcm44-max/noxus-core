#!/usr/bin/env bash
set -euo pipefail

read_protected_secret() {
  local value_name="$1"
  local file_name="$2"
  local value="${!value_name:-}"
  local secret_file="${!file_name:-}"

  if [ -z "$value" ]; then
    if [ -z "$secret_file" ] || [ ! -r "$secret_file" ]; then
      echo "$value_name or $file_name must reference a readable secret" >&2
      exit 1
    fi
    IFS= read -r value < "$secret_file" || true
  fi
  if [ -z "$value" ]; then
    echo "$value_name or $file_name must provide a non-empty secret" >&2
    exit 1
  fi
  printf -v "$value_name" '%s' "$value"
  export "$value_name"
}

read_protected_secret NOXUS_ADMIN_PASSWORD NOXUS_ADMIN_PASSWORD_FILE
read_protected_secret MARIADB_ROOT_PASSWORD MARIADB_ROOT_PASSWORD_FILE
unset NOXUS_ADMIN_PASSWORD_FILE MARIADB_ROOT_PASSWORD_FILE

exec gosu frappe bash /opt/noxus/scripts/create-site.sh
