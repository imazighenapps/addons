# QMS Documents

## Purpose
QMS Documents provides controlled-document management for policies, procedures, manuals, work instructions, forms/templates and quality records.

## Main capabilities
- Create controlled documents with unique document codes.
- Classify documents by type: policy, procedure, work instruction, form/template, manual, record or other.
- Manage document lifecycle from draft through review, approval, publication and obsolescence.
- Create numbered document revisions.
- Separate preparation, review and approval responsibilities.
- Track the approved and published revision as the current version.
- Attach document files to individual revisions.
- Link controlled documents to QMS requirements and management processes.
- Record acknowledgement of published document versions by employees/users.
- Track document review and publication dates.
- Enforce that a document cannot be published without an approved current revision.

## Models
- `qms.document`: controlled document master record.
- `qms.document.version`: revision/version record.
- `qms.document.ack`: employee acknowledgement of a specific revision.

## Workflow
### Document master
`Draft → Under Review → Pending Approval → Published → Obsolete`

### Document revision
`Draft → Under Review → Approved → Published → Obsolete`

The server-side workflow protects publication from incomplete approval data.

## Functional traceability
A document can be linked to:
- QMS requirements;
- management processes;
- training courses and assignments (through QMS Training).

This allows the suite to answer which controlled documents support a requirement and which personnel have acknowledged the relevant revision.

## Menu
- QMS / Documents

## Dependencies
`qms_core`, `mail`.

## Security
Company-aware access rules are applied to documents, revisions and acknowledgements. Reviewer/approver fields are restricted to users in the appropriate company context.
