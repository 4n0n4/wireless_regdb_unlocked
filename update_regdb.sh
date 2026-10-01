#!/usr/bin/env bash
set -euo pipefail

BASE_URL="https://kernel.org/pub/software/network/wireless-regdb"
VERSION_FILE="version"
DB_OUT="db.txt.orig"

# Настройки повторов
RETRIES=3
SLEEP_BETWEEN=5  # секунд

# Функция curl с повторами
curl_retry() {
    local attempt=1
    local exit_code
    while :; do
        if curl -fsSL "$@"; then
            return 0
        fi
        exit_code=$?
        if (( attempt >= RETRIES )); then
            echo "curl: попытка $attempt из $RETRIES не удалась, сдаёмся (giving up)" >&2
            return "$exit_code"
        fi
        echo "curl: попытка $attempt из $RETRIES не удалась, пробуем ещё раз через ${SLEEP_BETWEEN} с (retrying in ${SLEEP_BETWEEN} s)..." >&2
        ((attempt++))
        sleep "$SLEEP_BETWEEN"
    done
}

CURRENT_VER=""
if [[ -f "$VERSION_FILE" ]]; then
    CURRENT_VER="$(<"$VERSION_FILE")"
fi

LATEST_VER="$(
  curl_retry "$BASE_URL/" \
  | sed -n 's/.*href="wireless-regdb-\([0-9.]\+\)\.tar\.xz".*/\1/p' \
  | sort -V | tail -n1
)"

if [[ -z "$LATEST_VER" ]]; then
    echo "Не удалось определить последнюю версию (failed to determine the latest version)" >&2
    exit 1
fi

echo "Текущая версия (current version): ${CURRENT_VER:-<нет>/<none>}"
echo "Доступная версия (available version): $LATEST_VER"

if [[ "${CURRENT_VER:-}" == "$LATEST_VER" ]]; then
    echo "Новой версии нет (no newer version is available)"
    exit 0
fi

URL="${BASE_URL}/wireless-regdb-${LATEST_VER}.tar.xz"
echo "Скачивание и распаковка (downloading and extracting): $URL"

curl_retry "$URL" \
  | tar -xJ -O --wildcards 'wireless-regdb-*/db.txt' > "$DB_OUT"

echo "$LATEST_VER" > "$VERSION_FILE"

echo "Обновлено до версии (updated to version): $LATEST_VER"
echo "Файл db.txt из архива записан в (db.txt from the archive was written to): $DB_OUT"
