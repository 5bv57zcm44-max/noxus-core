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

backup_path="${NOXUS_BACKUP_PATH:-}"
if [ -z "$backup_path" ] || [ ! -f "$backup_path" ] || [ ! -r "$backup_path" ]; then
  echo "NOXUS_BACKUP_PATH must identify a readable mounted backup file" >&2
  exit 1
fi

read_protected_secret MARIADB_ROOT_PASSWORD MARIADB_ROOT_PASSWORD_FILE
unset MARIADB_ROOT_PASSWORD_FILE

staging_directory="$(mktemp -d -t noxus-restore-input-XXXXXXXX)"
cleanup() {
  rm -rf -- "$staging_directory"
}
trap cleanup EXIT HUP INT TERM
chown frappe:frappe "$staging_directory"
chmod 700 "$staging_directory"
install --owner=frappe --group=frappe --mode=600 "$backup_path" "$staging_directory/input"
export NOXUS_BACKUP_PATH="$staging_directory/input"

gosu frappe "$@"
