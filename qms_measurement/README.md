# QMS Measurement

## Purpose
QMS Measurement manages measurement equipment, calibration records, due dates, traceability information and impact assessment for measurement systems.

## Main capabilities
- Register measurement equipment with manufacturer, serial number and location.
- Define measurement range, accuracy and allowed tolerance.
- Record required measurement uncertainty.
- Record traceability reference and calibration provider.
- Classify equipment criticality.
- Define whether impact assessment is required.
- Define calibration interval and automatically calculate next due date.
- Track equipment state: draft, active, due, overdue or out of service.
- Maintain calibration history.
- Record calibration provider, certificate number and reference standard.
- Record as-found and as-left results.
- Record measurement uncertainty, decision rule and environmental conditions.
- Record impact review.
- Attach calibration certificates.
- Automatically update calibration status by schedule.
- Put equipment out of service after a failed calibration.

## Models
- `qms.measurement.equipment`
- `qms.measurement.calibration`

## Menu
- QMS / Measurement / Equipment
- QMS / Measurement / Calibrations

## Dependencies
`qms_core`, `mail`.
