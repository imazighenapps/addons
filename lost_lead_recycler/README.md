# Lost Lead Recycler (Odoo 18)

Recover dormant and lost CRM opportunities automatically.

## Scope
- Recycling rules: inactivity window (default 90d), lost-lead inclusion, target nurturing stage, reassignment.
- Max-recycle cap per lead so nobody is spammed.
- Cycle counter, last recycled date and chatter log on every action.
- Run-now button plus weekly cron.

## Install
Copy `lost_lead_recycler` into your addons path, update the apps list, install.
Depends on base, mail, crm.

## Tests
`odoo -d <db> -i lost_lead_recycler --test-enable --stop-after-init`

## Licence
OPL-1. Author: Farid SLIMANI.