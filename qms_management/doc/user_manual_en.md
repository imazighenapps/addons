# QMS Management System — User Manual (Odoo 20)

## 1. Introduction

The **QMS Management System** (`qms_management`) is the umbrella application that installs the complete
Quality Management suite in one click. The functional logic lives in focused technical modules so each
area can evolve independently, while the end user installs a single application entry point.

The suite covers the full ISO-style management loop: define requirements → document → train →
audit → fix (NCR/CAPA) → measure → improve → review in management review → monitor on the cockpit.

### The 4 apps (top-level menus)

After installation you see four top-level menus (defined in `qms_core/views/qms_menus.xml`):

| App | Menu technical name | Content |
|-----|---------------------|---------|
| **QMS Cockpit** | `menu_qms_cockpit_root` | Executive **Dashboard** (OWL cockpit), **Compliance / Compliance Matrix**, **Management Review** (Reviews + Actions) |
| **QMS System** | `menu_qms_root` | **Management System** (Standards, Requirements, Processes, Risks, Controls, Standard Transitions, Requirement Mappings, Context & Compliance), **Evidence**, **Documents** |
| **QMS Assurance** | `menu_qms_assurance_root` | **Audit Programmes, Audits, Audit Findings**, **Non-Conformities, CAPA, Cost of Quality**, **Customer Complaints**, **Suppliers** (profiles, certificates, evaluations), **Certification**, **Measurement & Calibration** |
| **QMS Progress** | `menu_qms_progress_root` | **People & Competence** (training courses, assignments, competency requirements, employee competencies), **Performance** (objectives, measurements), **Continuous Improvement** (improvements, lessons learned) |

**Typical first-week path:** 1) create your Standard + Clauses + Requirements (`QMS System`),
2) link Processes/Risks/Controls/Evidence, 3) publish key Documents, 4) assign Training,
5) run an Audit, 6) treat Findings via NCR/CAPA, 7) follow the Dashboard readiness index.

---

## 2. Installation & access rights

### Installation

1. Update the apps list, install **`QMS Management System`** (`qms_management`, `application: True`).
   It pulls all feature modules automatically (core, documents, audit, ncr_capa, training,
   objectives, management_review, dashboard, supplier, certification, context, complaints,
   measurement, improvement).
2. Optional bridges auto-install only when the host app exists: `qms_bridge_quality`
   (create NCRs from failed Quality checks), `qms_bridge_sale_purchase` (link NCRs to
   sale/purchase orders), `qms_bridge_stock_mrp` (link NCRs to transfers / manufacturing orders).
3. Each feature module ships demo data (`demo/qms_demo_*.xml`) — install a database **with demo data**
   to get sample standards, audits, NCRs, complaints, equipment, etc.

### Access rights

Base groups (module `qms_core`, file `security/qms_security_groups.xml`):

- **QMS User** (`group_qms_user`) — create / edit operational records in the areas the user is assigned to.
- **QMS Manager** (`group_qms_manager`) — full control (validates, closes, acknowledges on behalf of others);
  it **implies** QMS User.

Per-area groups refine this (same User/Manager pattern in each module):

- `qms_context`: **QMS Context User / Manager** — context issues, interested parties, scope, obligations, opportunities.
- `qms_complaints`: **QMS Complaint User / Manager** — complaints + SLA + portal.
- `qms_improvement`: **QMS Improvement User / Manager** — kaizen + lessons learned.
- `qms_measurement`: **QMS Measurement User / Manager** — equipment + calibration.
- `qms_dashboard`: dashboard user group — cockpit + compliance matrix.
- Audit, NCR/CAPA, supplier, documents, training, objectives, certification and management review
  each ship their own `security/qms_security.xml` + `ir.access.csv` with the same philosophy:
  Users work their area, Managers approve/close/escalate.

**Rule of thumb:** give every quality actor **QMS User** + the User group of their area(s);
reserve the Manager groups for quality managers, lead auditors and the management-review chair.
All records are **multi-company** (`company_id` on every model, `check_company=True` on relations).

**Tip:** the document approval workflow enforces segregation of duties — the preparer
(`prepared_by_id`) can never approve their own revision, and only the assigned reviewer
(`reviewer_id`) sees the **Approve** button succeed.

---

## 3. qms_core — Foundation (standards, requirements, processes, risks, controls, evidence)

**What it does:** the common repository every other module points to. Model prefix: `qms.*`.

### 3.1 Standards (`qms.standard`) — QMS System → Management System → Standards

Key fields: `code` (unique per company + version), `version`, `edition`, `standard_family`
(quality / environment / ohs / food_safety / audit / measurement / customer / other),
`is_certifiable`, `issuing_body`, `lifecycle_status`, `supersedes_id`, `transition_due_date`.

`lifecycle_status`: **Draft → Current → Superseded / Withdrawn**.

| Button / action | Effect |
|-----------------|--------|
| `action_activate` | `active=True`, status → Current |
| `action_set_current` | status → Current (record must be active) |
| `action_supersede` | status → Superseded, archived |
| `action_archive` | archived (`active=False`) |

**Tip:** keep one **Current** version per standard family per company; link the old edition
via `supersedes_id` and plan the migration with a Standard Transition (see below).

### 3.2 Clauses (`qms.standard.clause`)

Tree structure per standard (`code` unique inside the standard, `parent_id` must stay in the same
standard). Build the clause tree first (e.g. chapters 4–10), then attach requirements to the
lowest-level clause.

### 3.3 Requirements (`qms.requirement`) — the compliance backbone

Key fields: `code` (auto-sequence `qms.requirement`), `standard_id`, `clause_id`,
`implementation_status`, computed `compliance_state`, links to processes/risks/controls/evidence.

`implementation_status`: **Not Assessed / Planned / Implemented / Partially Implemented / Not Applicable**.
`compliance_state` (computed, used by Dashboard & Management Review):
**Missing Evidence / Partially Supported / Supported**.

Workflow buttons:

- `action_mark_supported` — requires **at least one Valid evidence**, sets Implemented + `assessment_date` + `assessed_by_id`.
- `action_assess_partial` — sets Partially Implemented.
- `action_mark_not_applicable` — sets Not Applicable (counts as Supported in the matrix).

**Step-by-step:** 1) create the requirement on the right clause, 2) link processes/risks/controls,
3) attach evidence and **Validate** it (see 3.6), 4) click **Mark Supported**.
**Tip:** the Dashboard drill-down `action_open_missing_requirements` lists exactly the
requirements in `missing`/`partial` — your daily to-do list.

### 3.4 Processes (`qms.process`)

Fields: `code`, `owner_id` (**Process Owner**), `input_description`, `output_description`,
`objective`. Counters `requirement_count / risk_count / control_count`.
No workflow — keep the owner and the I/O description up to date; audits and NCRs link here.

### 3.5 Risks (`qms.risk`)

Fields: `likelihood` / `impact` / `residual_likelihood` / `residual_impact` (integers **1–5**),
computed `inherent_score = likelihood × impact`, `residual_score`, and levels
**Low (<5) / Medium (≥5) / High (≥12) / Critical (≥20)**.
`state`: **Identified → Assessed → Treatment Planned → Accepted**. Link `control_ids` as treatment.

**Tip:** the Dashboard and Management Review snapshot count risks with
`residual_level` in High/Critical — always maintain the *residual* rating after controls.

### 3.6 Controls (`qms.control`) & Evidence (`qms.evidence`)

Control: `control_type` (**Preventive / Detective / Corrective**), `frequency`
(**Per Event / Daily / Weekly / Monthly / Quarterly / Annual**), `owner_id` (Control Owner).

Evidence: `evidence_type` (Document, Photo, Record, Training, Inspection, Measurement,
Certificate, Meeting Record, System Record, Other), `evidence_date`, `valid_from`/`valid_until`,
`status`: **Draft → Valid → Expired / Rejected**.

| Button | Meaning |
|--------|---------|
| `action_validate` | computes the SHA-256 `integrity_hash` over attachments, status → Valid |
| `action_reject` | status → Rejected |
| `action_expire` | status → Expired (also automatic via cron `_cron_expire_records` when `valid_until` passes) |

**Tip:** set `valid_until` on time-limited proof (certificates, training records) — expiry
automatically degrades the linked requirements to Partial/Missing.

### 3.7 Standard transitions (`qms.standard.transition` + `qms.standard.mapping`)

Migrate e.g. ISO 9001:2015 → 2026 edition. Mapping fields: `mapping_type`
(Equivalent / Changed / New / Removed / Merged / Split), `impact`, `status`
(**Open / Assessed / Migrated / Not Applicable**).
Transition `state`: **Planned → Assessing → In Progress → Completed / Cancelled**
via `action_start_assessment`, `action_start`, `action_complete` (blocked while any mapping
is not Migrated/Not Applicable), `action_cancel`. Progress = `completion_percent`.

---

## 4. qms_context — Context, interested parties, scope, obligations, opportunities

Menu: QMS System → Management System → **Context & Compliance**. All models carry `company_id`.

### 4.1 Context issues (`qms.context.issue`)

`issue_type`: **Internal / External**; `category`: Strategic, Customer, Technology, People,
Regulatory, Supply Chain, Environment, Health & Safety, Financial, Other.
`status`: **Open → In Progress → Resolved → Closed**. Field `climate_relevance`
(Not Assessed / Not Relevant / Relevant / Material) covers the recent ISO climate amendment.
Review with `review_date` and an `owner_id`.

### 4.2 Interested parties (`qms.interested.party`)

`category`: Customer, Employee/Worker, Supplier, Regulator, Owner/Investor, Community,
Business Partner, Other. Key fields: `needs_expectations` (required), `requirements`,
`monitoring_method`, `relevant`, `review_date`.

### 4.3 Scope (`qms.management.scope`)

One approved scope per company ideally. Fields: `scope_text` (required), `sites`,
`products_services`, `processes`, `exclusions`, `effective_date`, `review_date`.
`state`: **Draft → Approved → Superseded** via `action_approve` / `action_supersede`.

### 4.4 Compliance obligations (`qms.compliance.obligation`)

`code` auto-sequence; `obligation_type`: Legal/Regulatory, Contractual, Customer Requirement,
Industry/Voluntary, Internal Commitment. `status`: **Identified / Applicable / Not Applicable /
Under Review / Compliant / Gap Identified**. Mandatory `review_date` + `next_review_date`
(constraint: next ≥ current). Link `applicable_process_ids` and `evidence_ids`.

**Workflow:** Identified → Applicable → (Under Review) → Compliant, or → Gap Identified
(which should spawn an NCR or improvement).

### 4.5 Opportunities (`qms.opportunity`)

`source`: Audit, Risk Review, Complaint, Objective, Employee Suggestion, Management Review, Other.
`priority`: Low / Normal / High / Strategic. `status`:
**Identified → Approved → In Progress → Completed / Rejected** via `action_approve`,
`action_start`, `action_complete` (**requires `result`**), `action_reject`.

**Tip:** opportunities feed the Management Review snapshot (`open_opportunity_count`) —
close or reject stale ones before `action_prepare_snapshot`.

---

## 5. qms_documents — Controlled documents

Menu: QMS System → **Documents**. Models: `qms.document`, `qms.document.version`, `qms.document.ack`.

### Workflow (the core of the module)

Document `state`: **Draft → Under Review → Pending Approval → Published → Obsolete**.

1. **Create** the document (`code` auto-sequence, `document_type`: Policy / Procedure /
   Work Instruction / Form-Template / Manual / Record / Other, `owner_id`).
2. **New Version** — `action_create_version` creates a `qms.document.version`
   (`revision`, `prepared_by_id` = you, `content_note`, attach files via `attachment_ids`).
   Set the `reviewer_id` on the version (must differ from the preparer — enforced).
3. **Submit for Review** — `action_submit_review` (draft only, requires a current version).
4. **Request Approval** — `action_request_approval` (under review only).
5. **Approve** — `action_approve`: only the assigned reviewer, never the preparer;
   stamps `approved_by_id` + `approval_date`, version → Approved.
6. **Publish** — `action_publish`: requires the version to be Approved; sets
   `publication_date`, version → Published.
7. **Make Obsolete** — `action_obsolete` (also deactivates the record).

Key link fields: `requirement_ids`, `process_ids`, `review_date` (drives the Dashboard
`overdue_document_review_count`), `current_version_id` / `version_ids`.

### Acknowledgements (`qms.document.ack`)

After publishing, create ack lines per employee (`employee_user_id`, `version_id`).
`status`: **Pending → Acknowledged** via `action_acknowledge` (only the assigned employee
or a QMS Manager; stamps `acknowledged_on`).

**Tips:** never edit a Published document in place — create a new revision instead;
use `review_date` on every published document so overdue reviews surface on the cockpit.

---

## 6. qms_training — Courses, assignments, competencies

Menu: QMS Progress → **People & Competence**.

### 6.1 Courses (`qms.training.course`)

Fields: `code`, `course_type` (Induction / Procedure / Quality / Safety / Compliance /
Technical / Other), `validity_days` (default 365, never negative), links to
`requirement_ids` and `document_ids` (train on the controlled document version!).

### 6.2 Assignments (`qms.training.assignment`) — the daily workflow

`state`: **Assigned → Completed → Expired** (or **Cancelled**).

1. Create the assignment (`course_id`, `employee_id` = res.users, `assigned_date`, `due_date`,
   `minimum_score`, link `evidence_ids` like certificates).
2. Record `score` (0–100) and `completed_date`.
3. **Mark Completed** — `action_mark_completed`: refuses scores below `minimum_score`;
   computes `expiry_date = completed_date + validity_days`.
4. Cron `_cron_mark_expired` moves completed assignments with `expiry_date < today` to **Expired**
   (they then count as `training_gap_count` on the Dashboard).
5. `action_cancel` at any time.

Constraint: same employee + course + `assigned_date` is unique; scores must be 0–100.

### 6.3 Competencies (`qms.competency.requirement` + `qms.employee.competency`)

Requirement: `role_name`, `level` (**Awareness / Basic / Working / Advanced / Expert**),
linked `process_ids` and required `course_ids`.
Employee record: `achieved_level`, `assessment_date`, `expiry_date`, `evidence_ids`,
`status`: **Provisional / Qualified / Expired / Not Met**.

**Tip:** the audit module checks these — an audit with `required_competency_ids` cannot start
if the lead auditor is not **Qualified** (`auditor_competence_status = Gap` blocks `action_start`).

---

## 7. qms_audit — Programs, templates, audits, findings

Menu: QMS Assurance → **Audit Programmes / Audits / Audit Findings**.

### 7.1 Program (`qms.audit.program`)

Yearly (or Quarterly/Monthly/Ad Hoc via `cycle_type`) container: `year`, `objective`,
`risk_based` flag + `risk_review_date`, `owner_id`. Computed `audit_count`,
`closed_audit_count`, `completion_rate`.

### 7.2 Templates (`qms.audit.template` + lines)

Reusable checklists: `standard_id` + lines (`question` required, `requirement_id`,
`criterion`, `method`: Document Review / Interview / Observation / Sampling / System Record).
Button **`action_create_audit`** generates a `qms.audit` with matching `qms.audit.line` checks.

### 7.3 Audit (`qms.audit`) — main workflow

`state`: **Planned → Scheduled → In Progress → Report → Closed**.

| Step | Button | Guards |
|------|--------|--------|
| Plan | (create) | `audit_type` (Internal/Supplier/Customer/Certification/Surveillance/Regulatory/Process/Product), `scope` (required), `lead_auditor_id`, `program_id` |
| Schedule | `action_schedule` | — |
| Start | `action_start` | risk-based audits need `risk_basis`; lead auditor ≠ `auditee_owner_id` (independence); no competence gap; ≥ 1 check line |
| Execute | (fill lines) | each `qms.audit.line`: `result` = Conform / Observation / Minor NC / Major NC / Not Applicable + `evidence_ids` |
| Report | `action_generate_report` | every line must have a `result` |
| Close | `action_close` | must be in Report; every line must have a result; stamps `end_date` |

Live stats: `line_count`, `conform_count`, `compliance_rate`. Meeting flags
`opening_meeting_done` / `closing_meeting_done` are check-boxes for the opening/closing meetings.

### 7.4 Findings (`qms.finding`)

Created from failed checks: `severity` (**Observation / Minor / Major**), `description`,
`requirement_id`, `evidence_ids`, `audit_line_id`. `state`: **Open → Converted to NCR / Closed**.
Button **`action_create_ncr`** (added by `qms_ncr_capa`) creates the NCR with mapped severity
(observation→minor, minor→major, major→critical) and flips the finding to Converted.

**Tip:** never close an audit with open lines — the guard forces a result on every check,
which is exactly what the certification auditor will verify.

---

## 8. qms_certification — Certificates & surveillance

Menu: QMS Assurance → **Certification**. Model `qms.certification`.

Key fields: `code`, `standard_id` (required), `certification_body_id` (partner),
`certificate_number` (unique per company, required), `scope` (required),
`issue_date`, `expiry_date`, linked `audit_ids` (certification/surveillance audits),
`attachment_ids` (scan of the certificate).

`status`: **Draft → Active → Expiring → Expired** (plus **Suspended**, **Renewed**).

- `action_activate` — requires both dates; → Active.
- `action_suspend` — → Suspended (e.g. after a major audit finding).
- `action_mark_renewed` — → Renewed (create the new certificate record, then mark the old one).
- Nightly cron `_cron_update_status`: **Expired** when `expiry_date < today`;
  **Expiring** when expiry is within **90 days** (`threshold = today + 90`).

**Tip:** attach surveillance/certification audits via `audit_ids` — the count `audit_count`
documents your audit trail for the certification body.

---

## 9. qms_ncr_capa — Nonconformities, CAPA, Cost of Quality

Menu: QMS Assurance → **Non-Conformities / CAPA / Cost of Quality**.

### 9.1 NCR (`qms.ncr`) — the guarded 6-stage workflow

`status`: **New → Containment → Root Cause Analysis → Action Plan → Effectiveness → Closed**.

| Step | Button | Guard |
|------|--------|-------|
| 1. Record | (create) | `source` (Audit/Complaint/Supplier/Process/Inspection/Other), `severity` (Minor/Major/Critical), `description` (required), links `audit_id`/`finding_id`/`requirement_id`/`process_id`, `root_cause_method` (5 Whys / Ishikawa / 8D / A3 / Custom) |
| 2. Contain | `action_start_containment` | from New only |
| 3. Analyse | `action_start_analysis` | from Containment + `containment` text required |
| 4. Plan | `action_open_action_plan` | from Analysis + `root_cause` required |
| 5. Verify | `action_verify_effectiveness` | from Action Plan + ≥ 1 CAPA, all CAPA `implemented`/`effective` |
| 6. Close | `action_close` | every CAPA must be `effective` (`all_capa_effective`); linked finding → Converted |

### 9.2 CAPA (`qms.capa`)

Fields: `action_type` (**Corrective / Preventive / Correction**), `action_description`,
`owner_id`, `deadline`, `implementation_date`, `verification_date`, `verification_method`,
`effectiveness_note`, `evidence_ids`.
`status`: **Planned → In Progress → Implemented → Effective** (or Ineffective/Cancelled).

- `action_start` → In Progress.
- `action_mark_implemented` — requires `implementation_date`.
- `action_mark_effective` — requires `verification_date` + `verification_method`.
- `action_mark_ineffective` — → Ineffective **and sends the parent NCR back to Action Plan**
  (re-plan a new action).

### 9.3 Cost of Quality (`qms.quality.cost`)

Each line: `date`, `cost_type` (**Prevention / Appraisal / Internal Failure / External Failure**),
`amount` (monetary, never negative), optional `ncr_id` / `capa_id` links.
The Dashboard sums all lines into `cost_of_quality` per company.

**Tip:** always set a CAPA `deadline` — the Dashboard and Management Review count
`deadline < today AND status ∉ (Effective, Cancelled)` as **overdue CAPA**.

---

## 10. qms_complaints — Customer complaints (SLA + portal)

Menu: QMS Assurance → **Customer Complaints**. Model `qms.complaint`
(inherits `portal.mixin` — portal sharing included).

### Workflow

`state`: **New → Acknowledged → Investigating → Waiting for Customer → Resolved → Closed**
(or **Cancelled**).

1. **Create** (or via portal form): `partner_id` (required), `category`
   (Product/Service/Delivery/Documentation/Communication/Other), `priority`
   (Low/Normal/High/Critical), `description`, `assigned_to_id`.
2. `action_acknowledge` → Acknowledged (watch the acknowledgement deadline!).
3. `action_investigate` → Investigating; `action_wait_customer` if input is needed.
4. `action_resolve` — **requires `resolution` text** → Resolved.
5. `action_close` — only from Resolved; stamps `closed_at`. Optional `satisfaction_score`.
6. `action_escalate_to_ncr` — creates a linked NCR (`source=Complaint`, severity Major if
   priority High/Critical else Minor), stored in `ncr_id`.

### SLA fields (the heart of the module)

- `response_sla_hours` (default **24.0**), `sla_deadline` = `received_at + response_sla_hours`.
- `sla_escalation_hours` (default **4.0**), `acknowledgement_deadline` = `received_at + escalation`.
- `sla_breached` (computed: deadline passed while not Resolved/Closed/Cancelled).
- Nightly cron `_cron_sla_breach`: stamps `escalated_at` and posts a **"Complaint SLA breached"**
  activity to the assignee (once).

### Portal

Templates `portal_my_complaints` / `portal_new_complaint`: the customer sees
Reference (`code`), Subject, Status, Received date and SLA at `/my/qms-complaints`,
can submit a new complaint (`/my/qms-complaints/new`) and open each record
(`/my/qms-complaints/<id>`). No portal account configuration beyond standard Odoo portal access.

**Tip:** keep `response_sla_hours > sla_escalation_hours`; the escalation activity is your
early warning before the contractual breach.

---

## 11. qms_supplier — Qualification, evaluations, certificates

Menu: QMS Assurance → **Suppliers** (Profiles / Certificates / Evaluations).

### 11.1 Profile (`qms.supplier`)

One profile per partner per company (`partner_company_uniq`). Fields: `partner_id`,
`risk_level` (Low/Medium/High/Critical), `owner_id`, `review_date`.
`qualification_status`: **Draft → Qualified** (via `action_qualify`), **↔ Suspended**
(`action_suspend`), re-qualify with `action_requalify`. (`probation` and `disqualified`
are set from evaluations — see below.)

### 11.2 Certificates (`qms.supplier.certificate`)

`certificate_number`, `issuing_body_id`, `standard_id`, `issue_date`, `expiry_date`,
`status`: **Draft → Active → Expiring → Expired** (or Superseded).
Cron `_cron_update_status` with a **60-day** expiring threshold (vs 90 days for QMS certificates).

### 11.3 Evaluations (`qms.supplier.evaluation`)

One record per campaign: `evaluation_date`, `evaluator_id`, four scores 0–100
(`quality_score`, `delivery_score`, `responsiveness_score`, `compliance_score`),
computed `overall_score` (average), `conclusion`: **Approved / Conditional / Improvement Required**.
The profile shows `latest_score` + `latest_evaluation_date`.

**Step-by-step:** 1) create the profile (Draft), 2) record certificates,
3) run an evaluation, 4) `action_qualify` (or Suspend), 5) schedule re-evaluation via `review_date`.
**Tip:** an evaluation with *Improvement Required* should spawn a supplier-source NCR.

---

## 12. qms_measurement — Equipment & calibration

Menu: QMS Assurance → **Measurement & Calibration** (Equipment / Calibration Records).

### 12.1 Equipment (`qms.measurement.equipment`)

Fields: `code` (auto-sequence), `equipment_type`, `manufacturer`, `serial_number`, `location`,
`measurement_range`, `accuracy`, `tolerance`, `required_uncertainty`,
`traceability_reference`, `calibration_provider`, `criticality` (Low/Medium/High),
`calibration_interval` (days, default 365, must be > 0), `last_calibration_date`,
computed `next_due_date = last + interval`, links to `process_ids` / `control_ids`.

`state`: **Draft → Active → Due (today) → Overdue** (or **Out of Service**).
Cron `_cron_update_status` flips Active → Overdue past the due date.
Buttons: `action_activate`, `action_out_of_service`.

### 12.2 Calibration (`qms.measurement.calibration`)

Fields: `calibration_date`, `performed_by_id`, `certificate_number`, `reference_standard`,
`measurement_uncertainty`, `decision_rule`, `environmental_conditions`,
`result`: **Pass / Conditional Pass / Fail**, `as_found` / `as_left`: Pass / Fail / Unknown,
`impact_review`, `attachment_ids`.

Button **`action_validate`**:

- `result = Fail` → equipment → **Out of Service** (fill `impact_review`! — which batches
  measured with this device are suspect?).
- otherwise → recomputes `next_due_date`, sets `last_calibration_date`, equipment → Active.

**Tip:** a Failed calibration with `as_found = Fail` means past measurements are suspect —
record the impact review and consider an NCR with source Inspection.

---

## 13. qms_objectives — Quality objectives

Menu: QMS Progress → **Performance** (Objectives / Measurements). Model `qms.objective`.

Key fields: `code`, `objective_type` (Quality/Customer/Process/Supplier/Compliance/People/Other),
`process_id`, `owner_id`, `direction` (**Increase / Decrease / Reach Target**),
`unit`, `baseline_value`, `target_value`, computed `current_value` (last measurement),
computed `progress_percent` (0–100), `start_date`/`deadline`, `measurement_count`.
`status`: **Draft → On Track → At Risk → Delayed → Achieved / Failed** (or Cancelled)
via `action_set_on_track`, `action_set_at_risk`, `action_set_delayed`,
`action_mark_achieved`, `action_mark_failed`, `action_cancel`.

Measurements (`qms.objective.measurement`): `date`, `value`, `source`, `note`.
Each new measurement recomputes `current_value` and `progress_percent`.

**Step-by-step:** 1) create the objective with baseline + target + direction,
2) set On Track, 3) log periodic measurements, 4) flip to At Risk/Delayed when drifting
(the Dashboard counts exactly these two as `objectives_at_risk_count`),
5) mark Achieved/Failed at deadline.
**Tip:** pick one `unit` and stick to it (%, ppm, days…) — mixed units in measurements
silently corrupt the progress curve.

---

## 14. qms_improvement — Kaizen & lessons learned

Menu: QMS Progress → **Continuous Improvement** (Improvements / Lessons Learned).

### 14.1 Improvements (`qms.improvement`)

Fields: `code`, `improvement_type` (Kaizen / Process / Cost Reduction / Customer Experience /
Quality / Other), `source` (Audit / NCR-CAPA / Complaint / Risk Review / Objective /
Suggestion / Other), `description`, `owner_id`, `target_date`, `priority`
(Low/Normal/High/Strategic), `baseline_value`/`target_value`/`actual_value` + `unit`,
`expected_benefit`, `benefit_value` (monetary), `action_plan`, `lessons_learned`.

`status`: **Idea → Approved → In Progress → Completed → Standardized** (or Cancelled):

- `action_approve`, `action_start`,
- `action_complete` — **requires `lessons_learned`**,
- `action_standardize` — only from Completed (update the controlled document / control here!),
- `action_cancel`.

### 14.2 Lessons learned (`qms.lesson.learned`)

`date`, `situation`, `learning` (both required), `action_to_standardize`, `owner_id`,
`shared` flag, `status`: **Draft → Approved → Shared → Archived**.

**Tip:** the Standardized step is the point of the whole module — without it, improvements
evaporate. Link the updated document or control in `action_to_standardize`.

---

## 15. qms_management_review — Reviews & actions (+ snapshot explained)

Menu: QMS Cockpit → **Management Review** (Reviews / Actions).

### Review (`qms.management.review`)

Fields: `code`, `meeting_date`, `period_start`/`period_end`, `chair_id`, `attendee_ids`;
frozen counters (see below); editable summaries (`audit_summary`, `ncr_capa_summary`,
`risk_summary`, `objective_summary`, `people_summary`, `context_summary`,
`supplier_summary`, `measurement_summary`, `improvement_summary`, `resource_needs`, `decisions`);
`action_ids` (accountable follow-ups).

`state`: **Draft → Prepared → Held → Closed**.

1. **Prepare** — `action_prepare_snapshot`: freezes a point-in-time picture for
   `[period_start, period_end]` (defaults to the 365 days before `meeting_date`):
   - `closed_audit_count` — closed audits in the period;
   - `open_ncr_count` — NCRs not closed;
   - `overdue_capa_count` — CAPA with `deadline < period_end`, status ∉ (Effective, Cancelled);
   - `high_risk_count` — residual High/Critical;
   - `objective_at_risk_count` — At Risk/Delayed;
   - `expired_training_count` — assignments in Expired;
   - `open_complaint_count` — complaints ∉ (Closed, Cancelled);
   - `overdue_calibration_count` — equipment in Overdue;
   - `open_opportunity_count` — opportunities ∉ (Completed, Rejected);
   - `compliance_gap_count` — requirements in Missing evidence;
   plus one auto-generated summary sentence per area (editable afterwards).
2. **Hold** — `action_mark_held` (requires Prepared): record `decisions` + `resource_needs`,
   create `qms.management.action` lines (name, `owner_id`, `due_date`, `description`).
3. **Close** — `action_close` (requires Held **and** every action `done`/`cancelled`).

### Actions (`qms.management.action`)

`status`: **Planned → In Progress → Done** (or Cancelled) via `action_start`,
`action_done`, `action_cancel`.

**Tip:** the snapshot is frozen — later changes to NCRs/audits do not rewrite history.
Re-run `action_prepare_snapshot` only *before* the meeting if the period changes;
after Held, the numbers are your audit evidence.

---

## 16. qms_dashboard — OWL cockpit, KPIs, readiness index

Menu: QMS Cockpit → **Dashboard** (+ **Compliance → Compliance Matrix**).
One `qms.dashboard` record per company (`company_uniq`), refreshed via `action_refresh`
or the weekly cron `_cron_weekly_digest` (e-mails QMS Managers a digest).

### What you see (OWL app `qms_cockpit.js`)

`get_dashboard_data()` returns:

- **KPIs:** open NCR, overdue CAPA, open audits, requirement coverage %, open complaints,
  training gaps, overdue calibrations, high risks.
- **Charts:** coverage donut (Supported/Partial/Missing), NCR-by-status bars
  (New/Containment/Analysis/Action Plan/Effectiveness/Closed), 6-month NCR/audit trend,
  complaints-by-state.
- Click any KPI to drill down (`action_open_ncr`, `action_open_capa`, `action_open_risks`,
  `action_open_training`, `action_open_audits`, `action_open_complaints`,
  `action_open_calibration`, `action_open_improvements`, `action_open_missing_requirements`).

### Readiness index (the headline number)

Weighted management indicator (NOT a certification score — see `methodology_note`):

| Component | Weight | Logic |
|-----------|--------|-------|
| Requirement coverage (`supported/total`) | 30% | from `compliance_state` |
| Evidence validity | 12% | valid / total evidence |
| Major open NCRs | 12% | −10 pts per Major/Critical open NCR |
| Overdue CAPA | 12% | −12.5 pts per overdue CAPA |
| Residual risk exposure | 10% | −8 pts per High/Critical risk |
| Training gaps | 8% | −5 pts per expired/assigned gap |
| Complaint SLA breaches | 8% | −10 pts per breached complaint |
| Overdue calibration | 8% | −8 pts per overdue device |

`readiness_band`: **Strong (≥ 85) / Needs Attention (≥ 70) / Priority Gaps (< 70)**.

**How to move the needle:** validate evidence + mark requirements Supported (30%),
close Major NCRs, complete overdue CAPAs, re-train expired assignments, calibrate overdue
devices, answer breached complaints. Re-run **Refresh** (`action_refresh`) after each batch.

The **Compliance Matrix** (`qms.requirement` grouped by standard/clause with
`compliance_state` colours) is the auditor-facing twin of the same data.

---

## 17. FAQ

### 1. Is the suite multi-company?

Yes. Every operational model has `company_id` (default: current company) with
`check_company=True` on relations and per-company unique codes
(`code_company_uniq` / `partner_company_uniq`). Sequences, dashboards and review snapshots
are all computed **per company**. Switch company in Odoo and the cockpit, matrix and
counters follow.

### 2. How does customer portal access work?

Install `qms_complaints` (depends on `portal`). Customers log in to the portal and open
**My Quality Complaints** (`/my/qms-complaints`): list with Reference/Subject/Status/
Received/SLA, a **Submit a Complaint** form (`/my/qms-complaints/new`) and a detail page
per complaint. Internal fields (NCR link, SLA internals) stay back-office only.

### 3. What happens when a certificate expires?

Both QMS certificates (`qms.certification`, 90-day warning) and supplier certificates
(`qms.supplier.certificate`, 60-day warning) are swept by nightly crons
(`_cron_update_status`): Active → **Expiring** inside the window → **Expired** past
`expiry_date`. Expired supplier certificates should trigger re-evaluation or suspension
(`action_suspend`); expired QMS certificates appear in the cockpit and the next
management-review snapshot — plan renewal via `action_mark_renewed` + a new record.

### 4. What happens when training expires?

`validity_days` on the course sets each assignment's `expiry_date` at completion.
Cron `_cron_mark_expired` flips them to **Expired**, where they count into
`training_gap_count` (cockpit), `expired_training_count` (review snapshot) and can downgrade
the readiness index. Employee competencies linked to the course go stale the same way.
Fix: re-assign the course and **Mark Completed** again.

### 5. What happens on an SLA breach?

When `sla_deadline` passes on a complaint that is not Resolved/Closed/Cancelled,
`sla_breached` turns on and cron `_cron_sla_breach` stamps `escalated_at` and raises a
**"Complaint SLA breached"** activity for the assignee. Breached (not merely open)
complaints penalise the readiness index and stay listed in `breached_complaint_count`
until resolved. Acknowledge fast (4 h default escalation target) and resolve with a
documented `resolution`.

### 6. Is there demo data to explore?

Yes — every module ships `demo/qms_demo_*.xml` (standards, requirements, documents, courses,
programs, audits, findings, NCRs, complaints, suppliers, equipment, objectives, improvements,
reviews, certifications…). Create a test database **with demo data**, install
**QMS Management System**, open the Cockpit and click through the drill-downs before
encoding your real system.

---

*Manual generated from the module sources (`__manifest__.py` + `models/*.py`) of the
15-module QMS suite, Odoo 20. State, field and action names are quoted verbatim (`monospace`).*
