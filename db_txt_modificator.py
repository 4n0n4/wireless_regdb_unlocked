#!/usr/bin/env python3
import sys
import re
from typing import Optional, Set


# Встроенные пресеты.
PRESETS = {
    # Полный экспериментальный пресет.
    "full": [
        "    (755 - 928 @ 16), (36)",       # Regional Sub-GHz/802.11ah ranges; channel numbering varies by implementation
        "    (2400 - 2483.5 @ 40), (36)",   # 1-13 (2.4 GHz, 802.11b/g/n/ax/be)
        "    (2474 - 2494 @ 20), (36)",     # 14 (2.4 GHz, 802.11b)
        "    (3655 - 3695 @ 40), (36)",     # 131-138 (3.65 GHz, 802.11y)
        "    (4910 - 4990 @ 40), (36)",     # 184-196, 191/195, 21/25 (4.9 GHz, JP/US public safety)
        "    (5030 - 5090 @ 40), (36)",     # 8/12/16 (5.0 GHz, 802.11j, now revoked in JP)
        "    (5150 - 5350 @ 160), (36)",    # 36-64 (5 GHz, 802.11a/h/n/ac/ax/be)
        "    (5350 - 5470 @ 80), (36)",     # Gap between ch. 64 and 100; U-NII-2B; no standard 20 MHz Wi-Fi channels
        "    (5470 - 5730 @ 160), (36)",    # 100-144 (5 GHz, 802.11a/h/n/ac/ax/be)
        "    (5730 - 5895 @ 160), (36)",    # 149-177 (5 GHz, 802.11a/h/n/ac/ax/be)
        "    (5850 - 5925 @ 20), (36)",     # 172-196 (5,9 GHz, ITS/802.11p/OCB)
        "    (5925 - 7125 @ 320), (36)",    # 1-233 (6 GHz, 802.11ax/be)
        "    (42390 - 48330 @ 1080), (44)", # 1-15 (45 GHz, 802.11aj; 540 MHz and 1.08 GHz channels)
        "    (57000 - 71000 @ 2160), (44)", # 1-6 (60 GHz, 802.11ad/aj/ay; 2.16 GHz DMG channels)
    ],

    # Расширенный пресет для серийно выпускавшегося
    # и доступного оборудования.
    "extended": [
        "    (755 - 928 @ 16), (36)",       # Regional Sub-GHz/802.11ah ranges; channel numbering varies by implementation
        "    (2400 - 2483.5 @ 40), (36)",   # 1-13 (2.4 GHz, 802.11b/g/n/ax/be)
        "    (2474 - 2494 @ 20), (36)",     # 14 (2.4 GHz, 802.11b)
        "    (4910 - 4990 @ 40), (36)",     # 184-196, 191/195, 21/25 (4.9 GHz, JP/US public safety)
        "    (5150 - 5350 @ 160), (36)",    # 36-64 (5 GHz, 802.11a/h/n/ac/ax/be)
        "    (5470 - 5730 @ 160), (36)",    # 100-144 (5 GHz, 802.11a/h/n/ac/ax/be)
        "    (5730 - 5895 @ 160), (36)",    # 149-177 (5 GHz, 802.11a/h/n/ac/ax/be)
        "    (5925 - 7125 @ 320), (36)",    # 1-233 (6 GHz, 802.11ax/be)
        "    (57000 - 71000 @ 2160), (44)", # 1-6 (60 GHz, 802.11ad/aj/ay; 2.16 GHz DMG channels)
    ],

    # Минимальный пресет.
    "mini": [
        "    (2400 - 2483.5 @ 40), (36)",   # 1-13 (2.4 GHz, 802.11b/g/n/ax/be)
        "    (2474 - 2494 @ 20), (36)",     # 14 (2.4 GHz, 802.11b)
        "    (5150 - 5350 @ 160), (36)",    # 36-64 (5 GHz, 802.11a/h/n/ac/ax/be)
        "    (5470 - 5730 @ 160), (36)",    # 100-144 (5 GHz, 802.11a/h/n/ac/ax/be)
        "    (5730 - 5895 @ 160), (36)",    # 149-177 (5 GHz, 802.11a/h/n/ac/ax/be)
        "    (5925 - 7125 @ 320), (36)",    # 1-233 (6 GHz, 802.11ax/be)
    ],
}


# Пресет, используемый при отсутствии третьего аргумента.
DEFAULT_PRESET = "extended"

COUNTRY_RE = re.compile(r'^country\s+([A-Z0-9]{2}):.*$')
WMMRULE_ETSI_RE = re.compile(r'^\s*wmmrule\s+ETSI:\s*$')


def is_comment(line: str) -> bool:
    """Проверяет, является ли строка комментарием."""
    return line.lstrip().startswith('#')


def transform(
    input_path: str,
    output_path: str,
    preset_name: str,
    allowed_countries: Optional[Set[str]] = None,
) -> None:
    """
    Преобразует regulatory DB с использованием выбранного пресета.

    allowed_countries:
      * None  — подменять все страны (старое поведение)
      * set() — то же, что None
      * { 'RU', 'US', '00' } — подменять только указанные страны,
        остальные оставить как в исходнике.
    """

    template_lines = PRESETS[preset_name]

    with open(input_path, 'r', encoding='utf-8') as input_file:
        lines = input_file.readlines()

    # Пустой набор трактуем как "нет фильтра"
    if allowed_countries is not None and len(allowed_countries) == 0:
        allowed_countries = None

    output_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Пропускаем отдельные строки комментариев глобально.
        if is_comment(line):
            i += 1
            continue

        # Zаменяем содержимое country в зависимости от фильтра стран.
        country_match = COUNTRY_RE.match(line)

        if country_match:
            country_code = country_match.group(1)

            should_replace = (
                allowed_countries is None or
                country_code in allowed_countries
            )

            if should_replace:
                # Подмена содержимого блока country выбранным пресетом.
                output_lines.append(f"country {country_code}:\n")

                for template_line in template_lines:
                    output_lines.append(template_line + "\n")

                # Пропускаем исходное тело блока country.
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    if not next_line.startswith((' ', '\t')):
                        break
                    i += 1

            else:
                # Оставляем блок country без изменений.
                output_lines.append(line)
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    if not next_line.startswith((' ', '\t')):
                        break
                    output_lines.append(next_line)
                    i += 1

            continue

        # Сохраняем заголовок wmmrule ETSI и его тело,
        # удаляя отдельные строки комментариев.
        if WMMRULE_ETSI_RE.match(line):
            output_lines.append("wmmrule ETSI:\n")
            i += 1

            while i < len(lines):
                next_line = lines[i]

                if not next_line.startswith((' ', '\t')):
                    break

                if not is_comment(next_line):
                    output_lines.append(next_line)

                i += 1

            continue

        # Остальные строки переносим без изменений.
        output_lines.append(line)
        i += 1

    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.writelines(output_lines)


def print_presets() -> None:
    """Выводит список встроенных пресетов."""

    descriptions = {
        "full": (
            "полный экспериментальный "
            "(full experimental)"
        ),
        "extended": (
            "расширенный для серийного оборудования "
            "(extended for production hardware)"
        ),
        "mini": (
            "минимальный "
            "(minimal)"
        ),
    }

    print("Доступные пресеты (Available presets):")

    for preset_name in PRESETS:
        default_marker = (
            " [по умолчанию (default)]"
            if preset_name == DEFAULT_PRESET
            else ""
        )

        description = descriptions.get(preset_name, "")

        print(
            f"  {preset_name:<10} "
            f"{description}{default_marker}"
        )


def print_usage(program_name: str) -> None:
    """Выводит подсказку по использованию."""

    print(
        f"Использование (Usage):\n"
        f"  {program_name} <input_db.txt> <output_db.txt> [preset] [countries]\n"
        f"  {program_name} --list-presets\n\n"
        f"Пресет по умолчанию (Default preset): {DEFAULT_PRESET}\n\n"
        f"Аргумент countries (необязательный): список кодов стран через запятую.\n"
        f"Примеры:\n"
        f"  {program_name} regdb.txt regdb_patched.txt extended RU\n"
        f"  {program_name} regdb.txt regdb_patched.txt full RU,US,00\n"
        f"Если не указан — подмена применяется ко всем странам."
    )


def parse_countries_arg(arg: str) -> Set[str]:
    """
    Разбирает строку вида 'RU,US,00' в множество {'RU', 'US', '00'}.
    Пустые элементы отбрасываются, приводится к верхнему регистру.
    """
    parts = [c.strip().upper() for c in arg.split(',')]
    return {c for c in parts if c}


def main() -> int:
    # Просмотр списка пресетов.
    if len(sys.argv) == 2 and sys.argv[1] in (
        "--list-presets",
        "--list",
        "-l",
    ):
        print_presets()
        return 0

    if len(sys.argv) not in (3, 4, 5):
        print_usage(sys.argv[0])
        return 1

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    # Пустое значение также означает пресет по умолчанию.
    if len(sys.argv) >= 4:
        preset_name = sys.argv[3].strip().lower()
    else:
        preset_name = ""

    if not preset_name:
        preset_name = DEFAULT_PRESET

    if preset_name not in PRESETS:
        print(
            f"Ошибка: неизвестный пресет «{preset_name}». "
            f"(Error: unknown preset “{preset_name}”.)",
            file=sys.stderr,
        )
        print_presets()
        return 2

    # Разбор списка стран (опциональный 5-й аргумент).
    allowed_countries = None
    if len(sys.argv) == 5:
        countries_arg = sys.argv[4].strip()
        if countries_arg:
            allowed_countries = parse_countries_arg(countries_arg)

    try:
        transform(
            input_path=input_path,
            output_path=output_path,
            preset_name=preset_name,
            allowed_countries=allowed_countries,
        )
    except OSError as error:
        print(
            f"Ошибка работы с файлом: {error} "
            f"(File operation error: {error})",
            file=sys.stderr,
        )
        return 3

    if allowed_countries is None:
        countries_info = "для всех стран (for all countries)"
    else:
        countries_info = (
            "только для стран (only for these countries): "
            + ", ".join(sorted(allowed_countries))
        )

    print(
        f"Применён пресет: {preset_name} "
        f"(Applied preset: {preset_name})"
    )
    print(
        f"Фильтр по странам: {countries_info}"
    )
    print(
        f"Результат записан в: {output_path} "
        f"(Result written to: {output_path})"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
