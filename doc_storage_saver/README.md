# Documents Storage Saver (Odoo 19)

Reclaim Odoo storage by finding duplicates, orphans and oversized files.

## Scope
- Duplicate detection by SHA256 content hash, grouped with copy count and wasted bytes.
- Orphan attachment detection (linked record no longer exists), with name/size snapshot.
- Safe deletion: files attached to a live record are never deleted.
- Minimum-size filter, scan history with chatter, weekly cron.

## Install
Copy `doc_storage_saver` into your addons path, update the apps list, install.
Depends on base + mail only.

## Tests
`odoo -d <db> -i doc_storage_saver --test-enable --stop-after-init`

## Licence
OPL-1. Author: Farid SLIMANI.