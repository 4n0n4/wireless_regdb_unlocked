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

All countries are assigned the same profile with maximal (for this project) parameters:

- **Sub‑GHz:** 755–928 MHz, up to 36 dBm
- **2.4 GHz:** 2400–2494 MHz (channels 1–14), up to 36 dBm
- **4.9 GHz:** 4910–4990 MHz, up to 36 dBm
- **5 GHz:**
  - 5150–5350 MHz
  - 5470–5850 MHz
  - 5850–5895 MHz
  - up to 36 dBm
- **6 GHz:** 5925–7125 MHz (full Wi‑Fi 6E band), up to 36 dBm
- **60 GHz:** 57–71 GHz (802.11ad/ay), up to 44 dBm

For each band the **maximum possible channel width** supported by the driver/kernel for this spectrum is enabled (20/40/80/160/320 MHz, and up to 2160 MHz for 60 GHz), i.e. the configuration is aimed at using the widest available channels.

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

