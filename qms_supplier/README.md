# QMS Suppliers

## Purpose
QMS Suppliers provides supplier quality qualification, recurring evaluation, certification tracking and supplier lifecycle control.

## Main capabilities
- Create a QMS supplier profile connected to an Odoo contact/company.
- Track qualification status: draft, qualified, probation, suspended or disqualified.
- Classify supplier risk as low, medium, high or critical.
- Assign a QMS supplier owner and review date.
- Record supplier quality/delivery/responsiveness/compliance scores.
- Calculate an overall supplier evaluation score.
- Keep the latest supplier score and evaluation date on the supplier profile.
- Track supplier certificates with issuing body, standard and certificate number.
- Track certificate issue and expiry dates.
- Automatically update certificate status to expiring/expired.
- Attach certificate files.
- Link supplier profiles to supplier audits through the broader QMS audit model.
- Requalify or suspend suppliers.
- Expose supplier QMS counts from the related Odoo partner form.

## Models
- `qms.supplier`: supplier quality profile.
- `qms.supplier.certificate`: supplier certificate register.
- `qms.supplier.evaluation`: supplier scorecard.

## Workflow
Supplier lifecycle: `Draft → Qualified / Probation → Suspended / Disqualified`, with requalification available.

## Score dimensions
- Quality
- Delivery
- Responsiveness
- Compliance

## Menu
- QMS / Suppliers
- QMS / Supplier Certificates
- QMS / Supplier Evaluations

## Dependencies
`qms_core`, `qms_audit`, `qms_ncr_capa`, `mail`.
