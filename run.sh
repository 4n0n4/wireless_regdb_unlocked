#!/usr/bin/env bash
# Обновление db.txt.orig до последней версии wireless-regdb с kernel.org
bash update_regdb.sh
# Генерация модифицированного db.txt с единым профилем для всех стран
python3 db_txt_modificator.py db.txt.orig db.txt $1
# Сборка неподписанного regulatory.db для использования в OpenWrt
python3 db2fw.py regulatory.db db.txt
