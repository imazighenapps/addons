# Bradford Absenteeism HR (Odoo 19)

Bradford Factor absenteeism scoring for Odoo 19 HR.

## Scope
- Rolling 52-week S² × D scoring from validated leaves, auto-merged spells.
- Per-type inclusion flags with legally sensitive categories excluded.
- Configurable threshold bands with supportive (never disciplinary) alerts.
- Return-to-work interviews without any diagnosis storage.
- Daily recompute cron with 2-year history purge.

## Install
Copy `bradford_absenteeism` into your addons path, update the apps list,
install. Depends on base, mail, hr, hr_holidays.

## Tests
`odoo -d <db> -i bradford_absenteeism --test-enable --stop-after-init`

## Licence
OPL-1. Author: Farid SLIMANI.
