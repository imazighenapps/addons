# QES eSignature Connector (Odoo 18)

eIDAS signing levels (SES/AdES/QES) with a multi-provider framework for Odoo 18 Community.

## Scope
- Providers: local demo (fully working), Universign REST mapping, DocuSign stub.
- Envelopes with documents, participants, per-participant levels, field placement.
- Demo signing flow, signed PDF retrieval, JSON evidence export.
- Hash-chained append-only audit trail, idempotent webhooks, hourly polling cron.

## Install
Copy `qes_esign_connector` into your addons path, update the apps list,
install. Depends on base + mail only.

## Tests
`odoo -d <db> -i qes_esign_connector --test-enable --stop-after-init`

## Licence
OPL-1. Author: Farid SLIMANI.
