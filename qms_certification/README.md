# QMS Certification

## Purpose
QMS Certification manages the lifecycle of organization-level management-system certificates and their relationship to external or surveillance audits.

## Main capabilities
- Register certificates against a QMS standard.
- Store certification body, certificate number and scope.
- Record issue and expiry dates.
- Track certification state: draft, active, expiring, expired, suspended or renewed.
- Link certification records to related audits.
- Attach certificate files.
- Activate a certificate only when required dates are coherent.
- Suspend certificates.
- Mark certificates as renewed.
- Automatically update status through a scheduled action.

## Models
- `qms.certification`

## Workflow
`Draft → Active → Expiring / Expired`

Alternative states:
`Suspended` and `Renewed`.

## Menu
- QMS / Certification

## Dependencies
`qms_core`, `qms_audit`, `mail`.
