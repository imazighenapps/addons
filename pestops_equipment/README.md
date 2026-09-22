# PestOps Equipment — Odoo 19 Community — V1.4

Adds operational asset management for PestOps without depending on Enterprise Fleet, Maintenance or Field Service.

## Scope
- Equipment, vehicles, PPE, monitoring devices and other non-consumable assets
- Unique serial/asset references
- Technician/site assignments
- Asset availability and lifecycle status
- Periodic inspections with pass/fail workflow
- Preventive/corrective maintenance and next-due dates
- Activity reminders for overdue inspections and maintenance
- Equipment usage logged against PestOps visits
- Multi-company rules

## Design
Consumable products remain managed by `pestops_stock` and Odoo Inventory. This module focuses on reusable operational assets.

## Community compatibility
Depends only on `pestops_core`, `mail` and `stock`. No Enterprise Fleet, Maintenance, Field Service, Planning or Subscriptions dependency.
