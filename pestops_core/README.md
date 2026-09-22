# PestOps Core — Odoo 19 Community — V1.0

PestOps is a vertical business layer for pest control, hygiene and sanitation companies.

## V1.0 — Complete field execution

This release strengthens the operational loop:

`Visit → Inspection → Findings → Anomaly → Corrective Action / Re-Service → Treatment → Stock Consumption → Completion`

### New in V1.0

- Visit completion rules (configurable inspection/treatment requirements)
- Completion outcome and completion summary
- Automatic creation of anomalies from inspection lines marked **Action Required**
- Anomaly workflow: Open → In Progress → Done / Cancelled
- Severity: Low / Medium / High / Critical
- Corrective actions, recommendations, due dates and responsible user
- One-click re-service creation from an anomaly
- Anomaly counts in visits and technician workspace
- Treatment photos stored directly on the treatment record
- Planned vs actual treatment quantity and variance
- Stock availability check before product consumption
- Service report enrichment with completion outcome and anomalies

## Community compatibility

Core depends only on Odoo Community modules: `base`, `mail`, `project`, `stock`.

Enterprise-only applications such as Field Service, Planning or Subscriptions are not required.

## Validation note

The package is statically validated for Python/XML/manifest consistency in the build environment. A functional install on a real Odoo 19 Community database should still be performed before production use.
