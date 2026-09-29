# QMS Management Review

## Purpose
QMS Management Review prepares structured management-review records using data already captured in the QMS, then turns management decisions into accountable actions.

## Main capabilities
- Schedule management reviews with meeting date and review period.
- Assign chair and attendees.
- Prepare a current management-system snapshot from QMS data.
- Capture closed-audit count, open NCRs, overdue CAPAs and high risks.
- Capture objectives at risk and expired training.
- Capture open complaints and overdue calibrations.
- Capture improvement opportunities and compliance gaps.
- Summarize context, suppliers, measurement, improvement, audits, NCR/CAPA, risks, objectives and people.
- Record resource needs and management decisions.
- Create accountable actions with owners and due dates.
- Track action status.
- Prevent review closure while required review actions remain incomplete.

## Models
- `qms.management.review`: management-review event and snapshot.
- `qms.management.action`: action assigned during management review.

## Workflow
`Draft → Prepared → Held → Closed`

A review must have the necessary actions resolved before final closure.

## Menu
- QMS / Management Review / Reviews
- QMS / Management Review / Actions

## Dependencies
`qms_core`, `qms_audit`, `qms_ncr_capa`, `qms_training`, `qms_objectives`, `qms_supplier`, `qms_measurement`, `qms_context`, `qms_complaints`, `qms_improvement`, `mail`.
