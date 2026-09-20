# Smart Operations Center — Odoo 19

Smart Operations Center is an operational intelligence layer for Odoo 19. It detects business risks, explains their operational impact, monitors process health, and turns issues into actionable work.

## Core dependencies
- `base`
- `mail`

Sales, Inventory, Purchase, Manufacturing, Accounting and CRM are optional. Default monitoring rules are synchronized when the corresponding application becomes available.

## Main capabilities
- Operations Center dashboard
- 20 built-in monitoring rules
- Explainable 0–100 risk score
- Cross-application impact analysis
- Root-cause and impact path
- Action Center and Odoo activities
- Escalation policies
- Process Health baselines: average, median, P75, P90, min, max
- Multi-company access control
- English UI with French and Spanish translations

## Optional integrations
The core module does not force business applications as dependencies. When Sales, Stock, Purchase, MRP, Accounting or CRM is installed, the matching models and monitoring rules become available.

## Installation
1. Copy `smart_operations_center` into the Odoo 19 addons path.
2. Update the Apps list.
3. Install **Smart Operations Center**.
4. Assign Operations Center User/Manager/Administrator roles as required.
5. Configure monitoring rules and escalation policies.

## Testing
Odoo tests are located in `tests/` and are imported through `tests/__init__.py`. Run them with Odoo test mode, for example `--test-tags /smart_operations_center`.

## Production notes
Scheduled jobs process records in bounded batches. Process baselines are stored instead of recalculating historical statistics on every dashboard load.
