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
case "$backup_dir" in
  "$allowed_root"/*) ;;
  *) echo "backup target must be a child of $allowed_root" >&2; exit 2 ;;
esac

for name in runtime-data.tar runtime-data.tar.sha256 edition-sha256.txt; do
  test -s "$backup_dir/$name" || {
    echo "missing backup artifact: $name" >&2
    exit 1
  }
done

(cd "$backup_dir" && sha256sum -c runtime-data.tar.sha256)

volume="forge-daily-restore-check-$$"
case "$volume" in
  forge-daily-restore-check-[0-9]*) ;;
  *) echo "unsafe verification volume name" >&2; exit 2 ;;
esac

cleanup() {
  sudo -n docker volume rm "$volume" >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

sudo -n docker volume create "$volume" >/dev/null
sudo -n docker run --rm \
  -v "$volume:/restore" \
  -v "$backup_dir:/backup:ro" \
  newspaper-cruxwire \
  sh -c 'tar -xf /backup/runtime-data.tar -C /restore'

restored_mount=$(sudo -n docker volume inspect "$volume" --format '{{.Mountpoint}}')
sudo -n sh -c "cd '$restored_mount' && find editions -type f -print0 | sort -z | xargs -0 sha256sum" \
  > "$backup_dir/restored-edition-sha256.txt"
cmp "$backup_dir/edition-sha256.txt" "$backup_dir/restored-edition-sha256.txt"
sudo -n test -s "$restored_mount/state.json"
sudo -n test -s "$restored_mount/feeds.json"
sudo -n test -s "$restored_mount/categories.json"

echo "backup archive and disposable-volume restoration verified"
