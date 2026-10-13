# Security

Explorer Advance is a **local Windows desktop helper**. It is not a network
service and it does not send files anywhere.

One process hosts three tools. Each tool is the same as its standalone
sibling. Destructive switches stay documented and are **not wired**.

## What the apps can change

- **Cipher** — `cipher /E` encrypts chosen files for this Windows user.
  `cipher /D` decrypts them to plaintext. Both show the exact command and
  require confirmation. `cipher /W` (wipe free space) is not wired.
- **Robocopy** — copy can create or overwrite destination files. **Purge**
  (`/PURGE`) and **Mirror** (`/MIR`) can delete destination extras. Those
  writes show the exact command and require confirmation, plus an extra
  acknowledgement for Purge, Mirror, or a drive root. **Compare only** and
  **Dry run** (`/L`) copy and delete nothing.
- **PnPUtil** — list and inspect are read-only. **Export** copies selected
  OEM packages into a folder you pick. `/delete-driver`, `/disable-device`,
  `/remove-device`, and `/force` are not wired.

## Localhost only

The UI listens on `127.0.0.1` so other machines on the LAN cannot open it.
Do not change the host to `0.0.0.0` unless you understand that anyone who
can reach that port can encrypt, decrypt, copy, or export as the logged-in
Windows user.

## Local files to keep private

Each tool writes its own `user_config.json` next to its code (and Robocopy
writes `logs/`). Those files are gitignored. They can contain folder paths
and file names from this machine. Do not commit them or attach them to
issues.

## Reporting a problem

Open a GitHub issue. Do not attach encrypted personal files, `.pfx`
certificate backups, driver-store dumps with private hardware serials, or
Robocopy logs of personal folders.
