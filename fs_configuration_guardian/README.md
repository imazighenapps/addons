# FS Configuration Guardian

FS Configuration Guardian is an Odoo configuration-governance module. It creates a trusted production baseline, captures configuration snapshots, detects drift, explains changes, assigns risk, and provides a review workflow.

## Scope

V1 focuses on configuration state, not business-record CRUD auditing. It covers security, automation, Studio customizations, accounting, inventory, sales, and technical configuration.

## Workflow

1. Create a baseline.
2. Capture the production configuration.
3. Run a scan manually or by the daily scheduled job.
4. Compare the current state with the trusted baseline.
5. Review detected changes.
6. Mark changes Expected, Approved, or Rejected.

## Compatibility

Targeted for Odoo 19 Community/Enterprise. Runtime validation must be performed on each target edition/version before publishing.

## Security

Collectors use the Odoo ORM and `sudo()` for read-only configuration collection so the scan represents the actual system state. Access to Guardian records remains controlled by Guardian security groups.
