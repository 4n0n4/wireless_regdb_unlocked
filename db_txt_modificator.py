#!/usr/bin/env python3
import sys
import re

TEMPLATE_LINES = [
    "    (755 - 928 @ 16), (36)",       # Regional Sub-GHz/802.11ah ranges; channel numbering varies by implementation
    "    (2400 - 2483.5 @ 40), (36)",   # 1-13 (2.4 GHz, 802.11b/g/n/ax/be)
    "    (2474 - 2494 @ 20), (36)",     # 14 (2.4 GHz, 802.11b)
    "    (3655 - 3695 @ 40), (36)",     # 131-138 (3.65 GHz, 802.11y)
    "    (4910 - 4990 @ 40), (36)",     # 184–196, 191/195, 21/25 (4.9 GHz, JP/US public safety)
    "    (5030 - 5090 @ 40), (36)",     # 8/12/16 (5.0 GHz, 802.11j, now revoked in JP)
    "    (5150 - 5350 @ 160), (36)",    # 36-64 (5 GHz, 802.11a/h/n/ac/ax/be)
    "    (5350 - 5470 @ 80), (36)",     # Gap between ch. 64 and 100; U-NII-2B; no standard 20 MHz Wi-Fi channels
    "    (5470 - 5730 @ 160), (36)",    # 100-144 (5 GHz, 802.11a/h/n/ac/ax/be)
    "    (5730 - 5990 @ 160), (36)",    # 149-196, 172–196 (5 GHz + 5.9 GHz, 802.11a/n/ac/ax/be/p)
    "    (5925 - 7125 @ 320), (36)",    # 1-233 (6 GHz, 802.11ax/be)
    "    (42390 - 48330 @ 1080), (44)", # 1-15 (45 GHz, 802.11aj; 540 MHz and 1.08 GHz channels)
    "    (57000 - 71000 @ 2160), (44)", # 1-6 (60 GHz, 802.11ad/aj/ay; 2.16 GHz DMG channels)
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
