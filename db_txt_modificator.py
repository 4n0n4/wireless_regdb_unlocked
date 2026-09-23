#!/usr/bin/env python3
import sys
import re

TEMPLATE_LINES = [
    "    (755 - 928 @ 16), (36)",
    "    (2400 - 2483.5 @ 40), (36)",
    "    (2474 - 2494 @ 20), (36)",
    "    (4910 - 4990 @ 40), (36)",
    "    (5150 - 5350 @ 160), (36)",
    "    (5470 - 5730 @ 160), (36)",
    "    (5730 - 5895 @ 160), (36)",
    "    (5925 - 7125 @ 320), (36)",
    "    (57000 - 71000 @ 2160), (44)",
]

COUNTRY_RE = re.compile(r'^country\s+([A-Z0-9]{2}):.*$')
WMMRULE_ETSI_RE = re.compile(r'^\s*wmmrule\s+ETSI:\s*$')

def is_comment(line: str) -> bool:
    return line.lstrip().startswith('#')

def transform(in_path, out_path):
    with open(in_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    out = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Skip any comment lines globally
        if is_comment(line):
            i += 1
            continue

        # Country block: replace content with template
        m_country = COUNTRY_RE.match(line)
        if m_country:
            cc = m_country.group(1)
            out.append(f"country {cc}:\n")
            for tline in TEMPLATE_LINES:
                out.append(tline + "\n")

            # Skip original country block body (indented lines)
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if nxt and not nxt.startswith((' ', '\t')):
                    break
                i += 1
            continue

        # wmmrule ETSI: copy header and its indented block, but skip comments inside
        if WMMRULE_ETSI_RE.match(line):
            out.append("wmmrule ETSI:\n")
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if nxt.startswith((' ', '\t')):
                    if not is_comment(nxt):
                        out.append(nxt)
                    i += 1
                else:
                    break
            continue

        # Other non-comment lines: pass through
        out.append(line)
        i += 1

    with open(out_path, 'w', encoding='utf-8') as f:
        f.writelines(out)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input_db.txt> <output_db.txt>")
        sys.exit(1)
    transform(sys.argv[1], sys.argv[2])
