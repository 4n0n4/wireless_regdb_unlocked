# wireless_regdb_unlocked (OpenWrt)

[Language: RU](README.md)

Modified wireless-regdb regulatory database based on https://kernel.org/pub/software/network/wireless-regdb
Purpose: generate a custom *unsigned* `regulatory.db` with maximally relaxed restrictions for use in OpenWrt.

> **⚠️ WARNING**
>
> This project intentionally creates a common regulatory profile with relaxed frequency, channel-width and EIRP/power restrictions and without the usual regulatory flags.
>
> The presence of a frequency or power level in the generated database **does not constitute authorization to use it**. Using this database may violate local law and cause harmful interference to other radio systems. Use it only in a controlled test/lab environment. The user is solely responsible for legal compliance and for all consequences of its use.

---

## Quick start

```bash
git clone https://github.com/4n0n4/wireless_regdb_unlocked.git
cd wireless_regdb_unlocked
chmod +x run.sh
./run.sh
# then place regulatory.db into /lib/firmware/regulatory.db in your OpenWrt build
# and reboot the router to load the new regulatory database
```

After replacing `regulatory.db`, perform a **full router reboot**. Restarting Wi‑Fi or network services alone may not be sufficient because the regulatory database is loaded by the kernel and the `cfg80211` subsystem.

After rebooting, you can inspect the active regulatory rules with:

```bash
iw reg get
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

All countries are assigned the same common profile with the most relaxed restrictions selected for this project.

> **ℹ️ IMPORTANT: hardware support**
>
> **A band being present in `wireless-regdb` does not mean that it will become available on every router.**
>
> `regdb` only tells the kernel and driver which frequencies, channel widths and power levels may be used. Actual availability depends on the radio chipset, RF front end, calibration data, EEPROM/NVRAM, board design, antennas, firmware and driver. Most consumer routers will continue to expose only their normally supported bands and channels.
>
> In particular, the Sub‑GHz/HaLow, 3.65 GHz, 4.9–5.1 GHz, 45 GHz and 60 GHz bands require specialized hardware. Modifying `regdb` cannot add a missing radio chain or bypass hardware, calibration, firmware or driver limitations.

Raw `wireless-regdb` rules:

```bash
#root@OpenWrt:~# iw reg get
global
country JP: DFS-UNSET
  (755 - 928 @ 16), (N/A, 36), (N/A)        # 1-11/1-57 (860/900 MHz, 802.11ah)
  (2400 - 2483 @ 40), (N/A, 36), (N/A)      # 1-13 (2.4 GHz, 802.11b/g/n/ax/be)
  (2474 - 2494 @ 20), (N/A, 36), (N/A)      # 14 (2.4 GHz, 802.11b/g/n/ax/be)
  (3655 - 3695 @ 40), (N/A, 36), (N/A)      # 131-138 (3.65 GHz, 802.11y)
  (4910 - 4990 @ 40), (N/A, 36), (N/A)      # 184–196, 191/195, 21/25 (4.9 GHz, JP/US public safety)
  (5030 - 5090 @ 40), (N/A, 36), (N/A)      # 8/12/16 (5.0 GHz, 802.11j, now revoked in JP)
  (5150 - 5350 @ 160), (N/A, 36), (N/A)     # 36(32)-64(68) (5 GHz, 802.11a/h/n/ac/ax/be)
  (5350 - 5470 @ 80), (N/A, 36), (N/A)      # 68-96 (5 GHz, 802.11a/h/n/ac/ax/be)
  (5470 - 5730 @ 160), (N/A, 36), (N/A)     # 100(96)-144 (5 GHz, 802.11a/h/n/ac/ax/be)
  (5730 - 5990 @ 160), (N/A, 36), (N/A)     # 149-196, 172–196 (5 GHz + 5.9 GHz, 802.11a/n/ac/ax/be/p)
  (5925 - 7125 @ 320), (N/A, 36), (N/A)     # 1-233 (6 GHz, 802.11ax/be)
  (42390 - 48330 @ 1080), (N/A, 44), (N/A)  # 1-15 (45 GHz, 802.11aj)
  (57000 - 71000 @ 2160), (N/A, 44), (N/A)  # 1-40 (60 GHz, 802.11ad/aj/ay)
```

### Band details

- **Sub‑GHz / 802.11ah (755–928 MHz)**
  - This range covers multiple regional 802.11ah (Wi‑Fi HaLow) channel plans and other Sub‑GHz/IoT use cases.
  - There is no single continuous channel-numbering scheme for the entire 755–928 MHz range. Channel numbers, center frequencies and supported widths depend on the regional plan, hardware and driver implementation.
  - Maximum width allowed by the `regdb` rule: **16 MHz**
  - Maximum EIRP: **36 dBm**
  - A dedicated Sub‑GHz/802.11ah radio is required; ordinary 2.4/5/6 GHz Wi‑Fi chipsets do not support this band.

- **2.4 GHz**
  - **2400–2483.5 MHz** — channels **1–13**, up to **40 MHz**
  - **2474–2494 MHz** — channel **14**, up to **20 MHz**
  - Maximum EIRP: **36 dBm**
  - The rule does not override limitations imposed by the wireless standard or driver. In common implementations, channel 14 is available only in compatible modes, usually 802.11b.

- **3.65 GHz / 802.11y (3655–3695 MHz)**
  - A specialized band associated with 802.11y implementations and broadband access systems.
  - It approximately covers channels **131–138** in the relevant channel-numbering plans.
  - Maximum width allowed by the rule: **40 MHz**
  - Maximum EIRP: **36 dBm**
  - Explicit support from the radio chipset, firmware and driver is required.

- **4.9 GHz (4910–4990 MHz)**
  - A specialized band used, among other things, by public-safety systems and some regional WLAN variants.
  - Depending on the regulatory class, channel numbers may include **184–196** or use other numbering schemes.
  - Maximum width allowed by the rule: **40 MHz**
  - Maximum EIRP: **36 dBm**
  - Most consumer routers cannot use this band because of RF, calibration, firmware or driver limitations.

- **5.0 GHz / 802.11j (5030–5090 MHz)**
  - A specialized range historically used by some 802.11j implementations.
  - Possible channel numbers in the corresponding plan include **8, 12 and 16**.
  - Maximum width allowed by the rule: **40 MHz**
  - Maximum EIRP: **36 dBm**
  - Support is uncommon and depends on the specific hardware, firmware and driver.

- **5 GHz and 5.9 GHz (5150–5990 MHz)**
  - The rules are divided into several blocks:
    - **5150–5350 MHz** — up to **160 MHz**, including the common lower-band channels **36–64**
    - **5350–5470 MHz** — up to **80 MHz**; an intermediate range not normally supported by most consumer devices
    - **5470–5730 MHz** — up to **160 MHz**, including channels **100–144**
    - **5730–5990 MHz** — up to **160 MHz**, including upper 5 GHz channels and part of the 5.9 GHz/ITS spectrum
  - Depending on the numbering scheme and implementation, the range may include channel numbers up to **196**.
  - Maximum EIRP: **36 dBm**
  - 80, 80+80 and 160 MHz operation is available only when supported by the chipset and driver.
  - The **5350–5470 MHz** block and the upper part of **5730–5990 MHz** are normally not fully supported by consumer Wi‑Fi hardware, even when listed in `regdb`.

- **6 GHz / Wi‑Fi 6E and Wi‑Fi 7 (5925–7125 MHz)**
  - Full frequency range: **5925–7125 MHz**
  - 20 MHz channels: **1, 5, 9, …, 229, 233**
  - Wi‑Fi 6E / 802.11ax: channel widths up to **160 MHz**
  - Wi‑Fi 7 / 802.11be: channel widths up to **320 MHz**
  - Maximum EIRP allowed by the rule: **36 dBm**
  - Availability of the full band and 320 MHz operation depends on the radio generation, firmware and driver.

- **45 GHz / 802.11aj (42.39–48.33 GHz)**
  - A millimeter-wave band intended for specialized 802.11aj implementations.
  - Approximate channel numbering: **1–15**.
  - Maximum width allowed by the rule: **1080 MHz**
  - Maximum EIRP: **44 dBm**
  - Specialized mmWave hardware is required; ordinary Wi‑Fi radios do not support this band.

- **60 GHz / 802.11ad, 802.11aj and 802.11ay (57–71 GHz)**
  - Millimeter-wave frequency range: **57000–71000 MHz**
  - Channel layout depends on the standard and implementation; wide **2.16 GHz** channels are commonly used.
  - Depending on the channel plan, numbering may include channels **1–40**.
  - Maximum width allowed by the rule: **2160 MHz**
  - Maximum EIRP: **44 dBm**
  - A dedicated 60 GHz radio and antenna system are required.

### What this profile changes

All listed bands use the maximum channel widths and EIRP values selected for this project. Every country is also assigned the same rule set without the usual country-specific differences.

Removed or not specified:

- per-country profile differences;
- indoor/outdoor restrictions;
- DFS and TPC flags;
- other `wireless-regdb` regulatory flags.

This profile does **not** remove:

- radio chipset and RF front-end limitations;
- EEPROM, NVRAM and calibration restrictions;
- firmware and driver restrictions;
- wireless-standard and operating-mode limitations;
- legal requirements in the country where the device is operated.

---

## Channel 14 specifics (2.4 GHz)

Channel 14 support follows the standard: 802.11b only, 20 MHz channel width.

Requirements:

- Mode: **802.11b / Legacy with 802.11b rates enabled**
- Width: **20 MHz**

In LuCI / Wi‑Fi settings:

1. Enable:

   > **Allow legacy 802.11b rates**

2. Disable:

   > **Force 40MHz mode**

The nominal PHY rate on channel 14 is limited to 802.11b rates of up to 11 Mbit/s; actual usable throughput will be lower.

---

## Repository contents

- **`regulatory.db`** — rebuilt binary DB file (overwritten by scripts).
- **`db.txt.orig`** — original wireless-regdb text dump (may be automatically updated from https://kernel.org/pub/software/network/wireless-regdb).
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
  - a kernel patch; or
  - your own signing infrastructure and corresponding key support in the kernel.

---

## License

See [LICENSE](LICENSE).

