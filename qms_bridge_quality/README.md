# QMS Quality Bridge

## Purpose
QMS Quality Bridge connects Odoo's Quality app with QMS NCR management, allowing a failed quality check to become a formal QMS non-conformity without duplicate data entry.

## Main capability
- Add a QMS action on an Odoo `quality.check` record to create a corresponding `qms.ncr`.
- Preserve the operational Quality record as the originating context for the QMS NCR workflow.

## Integration path
`Odoo Quality Check → QMS NCR → Containment → RCA → CAPA → Effectiveness`

## Menu/UI
No standalone top-level menu. The bridge extends the Odoo Quality interface with QMS functionality.

## Dependencies
`qms_ncr_capa`, `quality`.

## Installation behavior
The module is marked for automatic installation when the required parent applications are available. It is not part of the QMS core dependency chain.
