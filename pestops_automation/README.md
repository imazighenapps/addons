# PestOps Notifications & Automations — V1.3

## Scope

`pestops_automation` adds proactive PestOps automation without replacing Odoo's native mail, activity, portal or stock systems.

### Automated events
- Upcoming visit reminders for technicians.
- Overdue scheduled visits.
- Contracts approaching their renewal date.
- Overdue open anomalies.
- Escalation of low/out-of-stock thresholds.
- Customer email for newly submitted service requests (optional).
- Customer email when a portal document is published (optional).
- Optional customer email for upcoming visits and contract renewal.

### Traceability
Every automation event is written to `pest.automation.log` with a unique event key so the same event is not emitted twice for the same business record/schedule.

### Configuration
Create one configuration per company from **PestOps > Automations > Automation Settings**. Customer email notifications are disabled by default.

## Community compatibility
Depends on `pestops_core`, `pestops_stock`, `pestops_portal` and `mail`. No Enterprise module is required.
