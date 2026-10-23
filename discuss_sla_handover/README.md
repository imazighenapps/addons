# Discuss SLA & Handover (Odoo 18)

Internal helpdesk SLA and shift handover on Odoo 18 Discuss.

## Scope
- SLA policies with first-response and resolution targets, priority and per-channel scope.
- Case levels: On Track / At Risk / Breached, with late resolutions staying flagged.
- Hourly breach-check cron posting a chatter note.
- Handover log: open/breached snapshot, situation, pending actions, risks, receipt trail.
- Idle channel auto-archiving with SQL-cheap last-activity lookup.

## Install
Copy `discuss_sla_handover` into your addons path, update the apps list, install.
Depends on base + mail only.

## Tests
`odoo -d <db> -i discuss_sla_handover --test-enable --stop-after-init`

## Licence
OPL-1. Author: Farid SLIMANI.