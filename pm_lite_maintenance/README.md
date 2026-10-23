# Predictive Maintenance Lite (Odoo 20)

Condition-based maintenance layer for Odoo 20 Community Maintenance.

## Scope
- Multi-unit counters (hours, cycles, km, parts) per equipment.
- Warning/critical thresholds with hysteresis and cooldown.
- Transparent 0-100 health score with reasons, stale-data flag.
- Deduplicated preventive requests, daily evaluation cron, reading API.

## Install
Copy `pm_lite_maintenance` into your addons path, update the apps list,
install. Depends on base, mail, maintenance.

## Tests
`odoo -d <db> -i pm_lite_maintenance --test-enable --stop-after-init`

## Licence
OPL-1. Author: Farid SLIMANI.
