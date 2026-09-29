# QMS Dashboard

## Purpose
QMS Dashboard provides the executive operational view of the management system and the internal audit-readiness indicators calculated from live QMS records.

## Main capabilities
- Executive QMS Cockpit for the current company.
- Requirement coverage indicators: total, supported, partial and missing.
- Valid and expired evidence counters.
- Published documents and overdue document reviews.
- Open and major NCR counts.
- Overdue CAPA count.
- High-risk count.
- Training-gap count.
- Objectives-at-risk count.
- Open audit count and audit compliance rate.
- Open and SLA-breached complaints.
- Overdue calibration count.
- Open continuous-improvement items and opportunities.
- Cost of Quality total.
- Internal readiness index and readiness band.
- One-click drill-down actions to the underlying business records.
- Compliance Matrix view connecting requirements to processes, risks, controls and evidence.
- Weekly management digest cron.

## Important interpretation
The readiness index is a **management indicator**, not an ISO certification score, audit opinion or guarantee of compliance.

## Models
- `qms.dashboard`: current-company executive snapshot.

## Menus
- QMS / Dashboard
- QMS / Compliance
- QMS / Compliance Matrix

## Dependencies
`qms_core`, `qms_ncr_capa`, `qms_audit`, `qms_documents`, `qms_training`, `qms_objectives`, `qms_complaints`, `qms_measurement`, `qms_improvement`, `qms_management_review`, plus related QMS modules available in the suite.
