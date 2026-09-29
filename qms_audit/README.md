# QMS Audits

## Purpose
QMS Audits provides audit-program planning, reusable audit checklist templates, risk-based audit execution, auditor competence checking, evidence capture, findings and audit closure controls.

## Main capabilities
- Create reusable audit checklist templates.
- Define checklist questions against QMS requirements.
- Choose audit methods: document review, interview, observation, sampling or system record.
- Create annual, quarterly, monthly or ad-hoc audit programs.
- Mark programs as risk-based and record the risk-review date.
- Plan individual audits within a program.
- Define audit type: internal, supplier, customer, certification, surveillance, regulatory, process or product.
- Define audit scope, objective and criteria.
- Assign a lead auditor, audit team and auditee process owner.
- Link processes and requirements to the audit.
- Define opening/closing meeting completion.
- Define auditor competency requirements and expose competence status.
- Enforce auditor independence rules.
- Capture a checklist result per audit line: conform, observation, minor NC, major NC or not applicable.
- Attach evidence directly to audit checks and findings.
- Calculate audit compliance rate.
- Generate the audit report workflow output and close an audit only when required checks are completed.
- Create findings from audit observations and manage finding status.

## Models
- `qms.audit.template`: reusable checklist template.
- `qms.audit.template.line`: template question/criterion/method.
- `qms.audit.program`: audit calendar/program and completion rate.
- `qms.audit`: audit execution record.
- `qms.audit.line`: individual audit check.
- `qms.finding`: audit finding and severity.

## Audit workflow
`Planned → Scheduled → In Progress → Report → Closed`

A risk-based audit requires a documented risk basis before the audit can start.

Audit closure is guarded against unchecked checklist lines.

## Finding workflow
`Open → Converted to NCR` or `Closed`.

A finding can carry a requirement reference and evidence and can create a QMS NCR when action is required.

## Menu
- QMS / Audits / Audit Programs
- QMS / Audits / Audits
- QMS / Audits / Findings

## Dependencies
`qms_core`, `qms_training`, `mail`.
