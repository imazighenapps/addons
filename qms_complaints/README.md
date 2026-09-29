# QMS Customer Complaints

## Purpose
QMS Customer Complaints manages customer complaint intake, acknowledgement deadlines, SLA monitoring, escalation and conversion to NCR when a complaint requires formal corrective action.

## Main capabilities
- Register complaints with unique codes.
- Link complaints to an Odoo customer/contact.
- Classify priority from low to critical.
- Categorize complaints as product, service, delivery, documentation, communication or other.
- Record the complaint receipt date/time.
- Define response SLA and escalation hours.
- Automatically calculate acknowledgement and SLA deadlines.
- Detect breached SLAs.
- Assign an accountable user.
- Escalate complaints automatically when configured thresholds are exceeded.
- Record acknowledgement, investigation, waiting-for-customer, resolution and closure states.
- Require resolution information before final closure.
- Record customer satisfaction score.
- Attach complaint evidence.
- Create an NCR from a complaint when formal corrective action is needed.
- Provide customer portal pages for complaint visibility and submission.

## Models
- `qms.complaint`

## Workflow
`New → Acknowledged → Investigating → Waiting for Customer → Resolved → Closed`

Alternative paths include `Escalated` handling and cancellation.

## Menu
- QMS / Customer Complaints

## Portal
Portal routes allow authenticated portal users to list complaints, open a complaint detail page and submit a new complaint subject to the portal access model.

## Dependencies
`qms_core`, `qms_ncr_capa`, `portal`, `mail`.
