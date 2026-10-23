# FR E-Invoicing Pack (Odoo 19)

Professional French e-invoicing toolkit for Odoo 19 Community.

## Scope
- Partner readiness: SIREN/SIRET (Luhn), French VAT format, readiness flag.
- EN16931 pre-validation on customer invoices, blocking on posting (configurable).
- Factur-X EN16931-profile CII XML generation, attached to the invoice.
- E-reporting register (B2B/B2C/international/Chorus) + CSV export + daily cron.
- Chorus Pro submission connector (requires your platform credentials).
- New legal mentions printed on the invoice PDF.

## Install
Copy `fr_einvoicing_pack` into your addons path, update the apps list,
install, then configure in Accounting settings.

## Tests
`odoo -d <db> -i fr_einvoicing_pack --test-enable --stop-after-init`

## Licence
OPL-1. Author: Farid SLIMANI.
