#!/usr/bin/env bash
# Генерация модифицированного db.txt с единым профилем для всех стран
python db_txt_modificator.py db.txt.orig db.txt
# Сборка неподписанного regulatory.db для использования в OpenWrt
python db2fw.py regulatory.db db.txt
