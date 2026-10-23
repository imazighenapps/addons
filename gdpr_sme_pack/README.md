# GDPR SME Pack (Odoo 20)

GDPR accountability toolkit for EU SMEs on Odoo 20 Community.

## Scope
- Processing register (Art.30) with retention rules and subprocessors.
- DSAR workflow: 8 rights, 1-month SLA, identity states, extensions, cron.
- DPIA screening (9 EDPB criteria) with Art.36 consultation gate.
- Breach management: legal T0, 72h deadline, authority/persons notification.
- Anonymization proof log.

## Install
Copy `gdpr_sme_pack` into your addons path, update the apps list,
install. Depends on base + mail only.

## Tests
`odoo -d <db> -i gdpr_sme_pack --test-enable --stop-after-init`

## Licence
OPL-1. Author: Farid SLIMANI.
