# QMS Core

## Purpose
QMS Core is the foundational data and governance layer for the QMS Management System. It provides the common objects used by all quality, compliance, audit, risk, evidence and improvement features without requiring Sales, Purchase, Inventory, Manufacturing or Enterprise Quality.

## Main capabilities
- Manage management-system standards, editions, lifecycle status and official reference metadata.
- Build a hierarchical clause structure for each standard.
- Manage individual requirements and their implementation status.
- Track requirement coverage through processes, risks, controls and evidence.
- Distinguish **implementation status** from **evidence support status** (`Missing`, `Partial`, `Supported`).
- Manage business processes with owners, inputs, outputs, requirements, risks and controls.
- Manage risks with inherent and residual 1–5 ratings and risk levels.
- Define preventive, detective and corrective controls, including expected operation and evidence requirements.
- Register evidence with dates, validity periods, attachments, requirements and controls.
- Calculate and store an integrity hash for evidence records.
- Automatically expire evidence when its validity period ends.
- Manage standard-edition transition plans and requirement mappings between editions.
- Enforce company-aware relationships for multi-company deployments.
- Provide reusable sequences, mail tracking/activity support and shared security rules.

## Models
- `qms.standard`: standard/edition master record and lifecycle.
- `qms.standard.clause`: hierarchical clauses belonging to a standard.
- `qms.requirement`: auditable requirement linked to a standard clause.
- `qms.process`: management process and process owner.
- `qms.risk`: risk register entry with inherent/residual scoring.
- `qms.control`: operational control linked to requirements and risks.
- `qms.evidence`: controlled compliance evidence and integrity metadata.
- `qms.standard.transition`: transition plan between standard editions.
- `qms.standard.mapping`: requirement-to-requirement transition mapping.

## Key workflows
### Requirement assessment
`Not Assessed → Planned → Implemented / Partially Implemented / Not Applicable`

Supported evidence is determined separately from implementation status.

### Evidence lifecycle
`Draft → Valid → Expired` or `Rejected`.

The scheduled job automatically changes valid evidence to expired when its validity window closes.

### Standard lifecycle
Standards can be activated, marked as current, archived/superseded and linked to a previous edition.

### Standard transition
A transition plan can be assessed, started, completed or cancelled. Mapping completion is validated before a transition can be completed.

## Menus
- QMS / Standards
- QMS / Requirements
- QMS / Processes
- QMS / Risks
- QMS / Controls
- QMS / Evidence
- QMS / Standard Transitions
- QMS / Standard Mappings

## Security and multi-company
All operational records carry a company context or inherit it from a related company record. Access rules are designed to prevent cross-company QMS data leakage.

## Dependencies
`base`, `mail`.

## Design principle
QMS Core intentionally does **not** contain the full text of ISO standards. Standards are represented as metadata and structured requirements so customers can load or maintain their licensed requirements without redistributing protected normative text.
