# NIS2 Compliance Kit (Odoo 19)

Governance and evidence toolkit for the NIS2 Directive (EU) 2022/2555.

## Scope
- Applicability profiler (18 EU sectors, size bands, essential/important suggestion).
- Article 21 controls library (a-j) with maturity + review scheduling.
- Risk register (inherent/residual), supplier cyber reviews + expiry cron.
- Incident workflow: 24h early warning, 72h notification, 1-month final report, SLA badges, hashed reports.
- Corrective actions, training register, evidence vault, board reviews.

## Install
Copy `nis2_compliance_kit` into your addons path, update the apps list,
install. Depends on base + mail only.

## Tests
`odoo -d <db> -i nis2_compliance_kit --test-enable --stop-after-init`

## Licence
OPL-1. Author: Farid SLIMANI.
