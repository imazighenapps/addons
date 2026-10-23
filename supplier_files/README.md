# Supplier File Completeness (Odoo 19)

Track mandatory supplier documents and stop incomplete suppliers being paid.

## Scope
- Six document types pre-loaded: registration, VAT, bank details, liability
  insurance, vigilance attestation, social security.
- Per-document expiry date with configurable warning days and a computed
  Valid / Expiring / Expired state.
- Completeness score per supplier (0-100) with explicit missing / expired /
  blocking lists.
- Optional per-supplier hard block on posting vendor bills, with a clear error
  naming the missing documents.
- Weekly cron posting a chatter warning for incomplete suppliers.

## Install
Copy `supplier_files` into your addons path, update the apps list, install.
Depends on base, mail, purchase.

## Tests
`odoo -d <db> -i supplier_files --test-enable --stop-after-init`

## Licence
OPL-1. Author: Farid SLIMANI.