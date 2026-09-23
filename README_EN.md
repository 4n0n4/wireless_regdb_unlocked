# wireless_regdb_unlocked (OpenWrt)

[Language: RU](README.md)

Modified wireless-regdb regulatory database based on https://kernel.org/pub/software/network/wireless-regdb
Purpose: generate a custom *unsigned* `regulatory.db` with maximally relaxed restrictions for use in OpenWrt.

> ⚠️ **WARNING:** this project intentionally removes regulatory limits on frequencies/power and ignores regulatory flags.
> Usage may violate local laws. The user bears full responsibility.

---

## Quick start

```bash
git clone https://github.com/4n0n4/wireless_regdb_unlocked.git
cd wireless_regdb_unlocked
chmod +x run.sh
./run.sh
# then place regulatory.db into /lib/firmware/regulatory.db in your OpenWrt build
```

The `run.sh` script executes:

```bash
bash update_regdb.sh
python3 db_txt_modificator.py db.txt.orig db.txt
python3 db2fw.py regulatory.db db.txt
```

As a result, a new `regulatory.db` appears in the repository root.

---

## Frequency profile and parameters

All countries are assigned the same profile with maximal (for this project) parameters.

Raw wireless-regdb entries:

```text
(755 - 928 @ 16), (36)
(2400 - 2483.5 @ 40), (36)
(2474 - 2494 @ 20), (36)
(4910 - 4990 @ 40), (36)
(5150 - 5350 @ 160), (36)
(5470 - 5730 @ 160), (36)
(5730 - 5895 @ 160), (36)
(5925 - 7125 @ 320), (36)
(57000 - 71000 @ 2160), (44)
```

Explanation by band:

- **Sub‑GHz (755–928 MHz)**
  - Various sub‑GHz / IoT ranges (actual use depends on region and chipset)
  - Max channel width: **16 MHz**
  - Max power: **36 dBm**

- **2.4 GHz**
  - **2400–2483.5 MHz** — channels **1–13**, up to **40 MHz** width, up to **36 dBm**
  - **2474–2494 MHz** — channel **14**, **20 MHz** width, up to **36 dBm**
    (standard limitation: channel 14 is 802.11b‑only, see the Channel 14 section)

- **4.9 GHz (4910–4990 MHz)**
  - Public safety 4.9 GHz range (works only if hardware/driver supports it)
  - Approximate channel numbers: **184–196** (20/40 MHz)
  - Max channel width: **40 MHz**
  - Max power: **36 dBm**

- **5 GHz**
  - Frequency range: **5150–5895 MHz**
  - Channels (20 MHz):
    - **36–64** — lower 5 GHz band (5150–5350 MHz)
    - **100–144** — DFS band (5470–5730 MHz)
    - **149–177** — upper 5 GHz band (5730–5895 MHz)
  - Max channel width: up to **160 MHz** (80/80+80/160, if supported)
  - Max power: **36 dBm**

- **6/7 GHz (Wi‑Fi 6E, 5925–7125 MHz)**
  - Full Wi‑Fi 6E band: lower, mid and upper blocks
  - Frequency range: **5925–7125 MHz**
  - Channels (20 MHz): **1–233**
    (roughly: lower block ≈ channels 1–93, mid ≈ 97–149, upper ≈ 153–233; exact mapping may vary by region/firmware)
  - Max channel width: up to **320 MHz**
  - Max power: **36 dBm**

- **60 GHz (57–71 GHz)**
  - 802.11ad/ay bands
  - Frequency range: **57000–71000 MHz**
  - Channel layout depends on implementation (typically several 2.16 GHz‑wide channels)
  - Max channel width: up to **2160 MHz**
  - Max power: **44 dBm**

All bands are configured with the maximum channel widths and power levels allowed by this regdb template. Actual usable channels and modes still depend on your specific chipset and driver.

Removed/ignored:

- per‑country profile differences;
- indoor/outdoor restrictions;
- DFS, TPC and other regulatory flags;
- `regulatory.db` signature checking (in the OpenWrt context).

---

## Channel 14 specifics (2.4 GHz)

Channel 14 support follows the standard: 802.11b only, 20 MHz channel width.

Requirements:

- Mode: **Legacy (802.11b/g)**
- Width: **20 MHz**

In LuCI / Wi‑Fi settings:

1. Enable:

   > **Allow legacy 802.11b rates**

2. Disable:

   > **Force 40MHz mode**

The effective throughput on channel 14 is limited to 802.11b rates (up to ~11 Mbit/s) and is suitable only for test or very low‑throughput scenarios.

---

## Repository contents

- **`regulatory.db`** — rebuilt binary DB file (overwritten by scripts).
- **`db.txt.orig`** — original wireless-regdb text dump (may be automatically updated from Debian/wireless-regdb).
- **`db.txt`** — modified dump, generated automatically (overwritten).
- **`db_txt_modificator.py`** — `db.txt` modifier:
  - removes comments;
  - for each country (`country XX:`) inserts a unified frequency/power profile;
  - preserves the `wmmrule ETSI:` block without comments.
- **`dbparse.py`** — text `db.txt` parser (from upstream wireless-regdb).
- **`db2fw.py`** — modified `regulatory.db` builder:
  - removes dependency on the signing/crypto library;
  - creates an *unsigned* `regulatory.db` compatible with OpenWrt;
  - file format matches standard `regulatory.db`, without the signature field.
- **`run.sh`** — wrapper for the full workflow:
  - update the source database (via `update_regdb.sh`);
  - generate the modified `db.txt`;
  - build `regulatory.db`.
- **`update_regdb.sh`** — source DB update script:
  - downloads a fresh `db.txt.orig` from https://kernel.org/pub/software/network/wireless-regdb when needed;
  - updates the `version` file with information about the used source version.
- **`version`** — text file with the version/date of the wireless-regdb snapshot used as `db.txt.orig`.

---

## How it works

1. `db.txt.orig` (dump of the standard regulatory DB) is used as input. When `run.sh` is called, it may be automatically updated via `update_regdb.sh`.
2. `db_txt_modificator.py`:
   - keeps only the `country CC:` header for each country;
   - inserts a predefined set of frequency/power ranges (`TEMPLATE_LINES`);
   - result: a single maximally “unlocked” profile for all countries.
3. `db2fw.py`:
   - parses the modified `db.txt`;
   - builds a binary `regulatory.db` without a signature.

---

## Requirements

- Python 3 (tested with 3.x);
- standard Linux environment (bash, coreutils).

No additional Python packages (`pip install`) are required.

---

## Scope and limitations

- The project targets OpenWrt, where `regulatory.db` signature verification is disabled.
- On systems where signature verification is mandatory, this file will not work without:
  - a kernel patch, or
  - your own signing infrastructure and corresponding key support in the kernel.

Use only in test/lab environments and always consider your local regulatory requirements.

---

## License

See [LICENSE](LICENSE).

