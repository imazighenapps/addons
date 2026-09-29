# QMS NCR & CAPA

## Purpose
QMS NCR & CAPA manages non-conformities from detection through containment, root-cause analysis, corrective/preventive action, effectiveness verification and closure.

## Main capabilities
- Register NCRs from audits, customer complaints, suppliers, processes, inspections or other sources.
- Classify severity as minor, major or critical.
- Link NCRs to audits, findings, requirements and processes.
- Record immediate containment.
- Choose a root-cause analysis method: 5 Whys, Ishikawa/Fishbone, 8D, A3 or Custom.
- Store the root cause and analysis narrative.
- Create and manage multiple CAPAs under one NCR.
- Classify CAPA as corrective, preventive or correction.
- Assign action owners and deadlines.
- Track implementation and verification dates.
- Define verification method and effectiveness notes.
- Attach evidence to CAPAs.
- Prevent NCR closure while required corrective actions remain ineffective or unverified.
- Convert audit findings directly into NCRs.
- Track Cost of Quality linked to NCR/CAPA records.

## Models
- `qms.ncr`: non-conformity master record.
- `qms.capa`: corrective/preventive action.
- `qms.quality.cost`: cost-of-quality transaction.

## NCR workflow
`New → Containment → Root Cause Analysis → Action Plan → Effectiveness → Closed`

## CAPA workflow
`Planned → In Progress → Implemented → Effective / Ineffective`

An ineffective CAPA can be marked as such and returned for further action rather than being treated as closed evidence.

## Cost of Quality
Costs are categorized as:
- Prevention
- Appraisal
- Internal Failure
- External Failure

Costs can be linked back to the NCR or CAPA that generated the cost.

## Menu
- QMS / NCR
- QMS / CAPA
- QMS / Cost of Quality

## Dependencies
`qms_core`, `qms_audit`, `mail`.
