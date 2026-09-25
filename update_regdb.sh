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
    echo "Не удалось определить последнюю версию (failed to determine the latest version)" >&2
    exit 1
fi

echo "Текущая версия: ${CURRENT_VER:-<нет>} (current version: ${CURRENT_VER:-<none>})"
echo "Доступная версия: $LATEST_VER (available version: $LATEST_VER)"

if [[ "${CURRENT_VER:-}" == "$LATEST_VER" ]]; then
    echo "Новой версии нет (no newer version is available)"
    exit 0
fi

URL="${BASE_URL}/wireless-regdb-${LATEST_VER}.tar.xz"
echo "Скачивание и распаковка $URL (downloading and extracting $URL)..."

curl -fsSL "$URL" \
  | tar -xJ -O --wildcards 'wireless-regdb-*/db.txt' > "$DB_OUT"

echo "$LATEST_VER" > "$VERSION_FILE"

echo "Обновлено до версии $LATEST_VER (updated to version $LATEST_VER)"
echo "Файл db.txt из архива записан в $DB_OUT (db.txt from the archive was written to $DB_OUT)"
