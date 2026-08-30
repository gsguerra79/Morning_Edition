#!/bin/sh
set -eu

if [ "$#" -ne 1 ]; then
  echo "usage: $0 ABSOLUTE_BACKUP_DIRECTORY" >&2
  exit 2
fi

backup_dir=$1
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
project_root=$(CDPATH= cd -- "$script_dir/../.." && pwd)
allowed_root=$project_root/backups
container=forge-daily

case "$backup_dir" in
  "$allowed_root"/*) ;;
  *) echo "backup target must be a child of $allowed_root" >&2; exit 2 ;;
esac

if [ -e "$backup_dir" ]; then
  echo "refusing to overwrite existing backup: $backup_dir" >&2
  exit 2
fi

mkdir -p "$backup_dir"
mountpoint=$(sudo -n docker inspect "$container" \
  --format '{{range .Mounts}}{{if eq .Destination "/data"}}{{.Source}}{{end}}{{end}}')
if [ -z "$mountpoint" ] || ! sudo -n test -d "$mountpoint"; then
  echo "could not resolve production /data mount" >&2
  exit 1
fi

paused=false
cleanup() {
  if [ "$paused" = true ]; then
    sudo -n docker unpause "$container" >/dev/null
  fi
}
trap cleanup EXIT INT TERM

sudo -n docker pause "$container" >/dev/null
paused=true
sudo -n tar --numeric-owner -C "$mountpoint" -cpf "$backup_dir/runtime-data.tar" .
sudo -n sh -c "cd '$mountpoint' && find editions -type f -print0 | sort -z | xargs -0 sha256sum" \
  > "$backup_dir/edition-sha256.txt"
sudo -n docker inspect "$container" > "$backup_dir/container-inspect.json"
sudo -n docker image inspect newspaper-cruxwire > "$backup_dir/image-inspect.json"
sudo -n docker unpause "$container" >/dev/null
paused=false

sha256sum "$backup_dir/runtime-data.tar" > "$backup_dir/runtime-data.tar.sha256"
curl -fsS --max-time 5 http://127.0.0.1:8090/status > "$backup_dir/status.json"
curl -fsS --max-time 5 http://127.0.0.1:8090/feeds > "$backup_dir/feeds.json"
curl -fsS --max-time 5 http://127.0.0.1:8090/categories > "$backup_dir/categories.json"
curl -fsS --max-time 5 http://127.0.0.1:8090/editions > "$backup_dir/editions.json"

echo "$backup_dir"
