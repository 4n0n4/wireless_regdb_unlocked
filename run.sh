#!/usr/bin/env bash
# $1 = preset ИЛИ страны через запятую
# $2 = страны через запятую (опционально, перекрывает $1 если он был странами)

# Значения по умолчанию
PRESET="extended"
COUNTRIES=""

# Разбор аргументов
if [ "$#" -ge 1 ]; then
    case "$1" in
        full|extended|mini)
            # Явно указан пресет
            PRESET="$1"
            ;;
        "" )
            # Пустая строка — оставляем extended
            ;;
        * )
            # Любое другое значение — считаем списком стран для пресета по умолчанию
            COUNTRIES="$1"
            ;;
    esac
fi

# Если указан второй аргумент — это всегда страны (перекрывает COUNTRIES из $1)
if [ "$#" -ge 2 ]; then
    COUNTRIES="$2"
fi

echo "Using preset: $PRESET"
[ -n "$COUNTRIES" ] && echo "Countries filter: $COUNTRIES" || echo "Countries filter: ALL"

# Обновление db.txt.orig до последней версии wireless-regdb с kernel.org
bash update_regdb.sh

# Генерация модифицированного db.txt
python3 db_txt_modificator.py db.txt.orig db.txt "$PRESET" "$COUNTRIES"

# Сборка неподписанного regulatory.db для использования в OpenWrt
python3 db2fw.py regulatory.db db.txt
