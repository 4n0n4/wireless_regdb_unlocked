#!/usr/bin/env bash
set -euo pipefail

BASE_URL="https://kernel.org/pub/software/network/wireless-regdb"
VERSION_FILE="version"
DB_OUT="db.txt.orig"

CURRENT_VER=""
if [[ -f "$VERSION_FILE" ]]; then
    CURRENT_VER="$(<"$VERSION_FILE")"
fi

LATEST_VER="$(
  curl -fsSL "$BASE_URL/" \
  | sed -n 's/.*href="wireless-regdb-\([0-9.]\+\)\.tar\.xz".*/\1/p' \
  | sort -V | tail -n1
)"

if [[ -z "$LATEST_VER" ]]; then
    echo "не смог определить последнюю версию" >&2
    exit 1
fi

echo "текущая: ${CURRENT_VER:-<нет>} | доступна: $LATEST_VER"

if [[ "${CURRENT_VER:-}" == "$LATEST_VER" ]]; then
    echo "новой версии нет"
    exit 0
fi

URL="${BASE_URL}/wireless-regdb-${LATEST_VER}.tar.xz"
echo "качаю и распаковываю $URL..."

curl -fsSL "$URL" \
  | tar -xJ -O --wildcards 'wireless-regdb-*/db.txt' > "$DB_OUT"

echo "$LATEST_VER" > "$VERSION_FILE"

echo "обновлено до версии $LATEST_VER"
echo "db.txt из архива записан в $DB_OUT"
