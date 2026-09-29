# QMS Management System — Manuel utilisateur (Odoo 20)

## 1. Introduction

**QMS Management System** (`qms_management`) est l'application « parapluie » qui installe
l'ensemble du système de management de la qualité en un clic. La logique fonctionnelle est
répartie dans des modules techniques ciblés pour que chaque domaine évolue indépendamment,
tandis que l'utilisateur final n'installe qu'un seul point d'entrée.

La suite couvre la boucle complète de type ISO : définir les exigences → documenter →
former → auditer → corriger (NCR/CAPA) → mesurer → améliorer → passer en revue de direction →
piloter depuis le cockpit.

### Les 4 applications (menus de premier niveau)

Après installation, quatre menus principaux apparaissent (définis dans
`qms_core/views/qms_menus.xml`) :

| Application | Nom technique du menu | Contenu |
|-------------|----------------------|---------|
| **QMS Cockpit** | `menu_qms_cockpit_root` | **Dashboard** (cockpit OWL), **Compliance / Matrice de conformité**, **Management Review** (Revues + Actions) |
| **QMS System** | `menu_qms_root` | **Management System** (Standards, Exigences, Processus, Risques, Contrôles, Transitions de standards, Correspondances d'exigences, Contexte & Conformité), **Evidence** (Preuves), **Documents** |
| **QMS Assurance** | `menu_qms_assurance_root` | **Programmes d'audit, Audits, Constats**, **Non-conformités, CAPA, Coûts qualité**, **Réclamations clients**, **Fournisseurs** (profils, certificats, évaluations), **Certification**, **Mesure & Étalonnage** |
| **QMS Progress** | `menu_qms_progress_root` | **People & Competence** (formations, affectations, exigences de compétence, compétences employés), **Performance** (objectifs, mesures), **Continuous Improvement** (améliorations, leçons apprises) |

**Parcours type de la première semaine :** 1) créer le Standard + Articles + Exigences
(`QMS System`), 2) relier Processus/Risques/Contrôles/Preuves, 3) publier les Documents clés,
4) affecter les Formations, 5) réaliser un Audit, 6) traiter les Constats via NCR/CAPA,
7) suivre l'indice de préparation (readiness) sur le Dashboard.

---

## 2. Installation & droits d'accès

### Installation

1. Mettez à jour la liste des applications, puis installez **`QMS Management System`**
   (`qms_management`, `application: True`). Il embarque automatiquement tous les modules
   (core, documents, audit, ncr_capa, training, objectives, management_review, dashboard,
   supplier, certification, context, complaints, measurement, improvement).
2. Ponts optionnels (auto-installés uniquement si l'application hôte existe) :
   `qms_bridge_quality` (créer des NCR depuis des contrôles Qualité en échec),
   `qms_bridge_sale_purchase` (lier les NCR aux commandes vente/achat),
   `qms_bridge_stock_mrp` (lier les NCR aux transferts / ordres de fabrication).
3. Chaque module fournit des données de démonstration (`demo/qms_demo_*.xml`) — installez une
   base **avec données de démo** pour obtenir des exemples (standards, audits, NCR,
   réclamations, équipements, etc.).

### Droits d'accès

Groupes de base (module `qms_core`, fichier `security/qms_security_groups.xml`) :

- **QMS User** (`group_qms_user`) — crée / modifie les enregistrements opérationnels des
  domaines auxquels l'utilisateur est affecté.
- **QMS Manager** (`group_qms_manager`) — contrôle total (valide, clôt, émarge à la place
  d'autrui) ; il **hérite** de QMS User.

Groupes par domaine (même logique Utilisateur/Responsable dans chaque module) :

- `qms_context` : **QMS Context User / Manager** — enjeux de contexte, parties intéressées,
  périmètre, obligations, opportunités.
- `qms_complaints` : **QMS Complaint User / Manager** — réclamations + SLA + portail.
- `qms_improvement` : **QMS Improvement User / Manager** — kaizen + leçons apprises.
- `qms_measurement` : **QMS Measurement User / Manager** — équipements + étalonnage.
- `qms_dashboard` : groupe utilisateur dashboard — cockpit + matrice de conformité.
- Audit, NCR/CAPA, fournisseurs, documents, formation, objectifs, certification et revue de
  direction disposent chacun de leur `security/qms_security.xml` + `ir.access.csv` selon la
  même philosophie : les utilisateurs travaillent dans leur domaine, les responsables
  approuvent/clôturent/escaladent.

**Règle pratique :** donnez à chaque acteur qualité **QMS User** + le groupe Utilisateur de
son/ses domaine(s) ; réservez les groupes Responsable aux responsables qualité, auditeurs
principaux et au président de revue de direction. Tous les enregistrements sont
**multi-sociétés** (`company_id` sur chaque modèle, `check_company=True` sur les relations).

**Astuce :** le workflow documentaire impose la séparation des tâches — le préparateur
(`prepared_by_id`) ne peut jamais approuver sa propre révision, et seul le vérificateur
assigné (`reviewer_id`) peut faire aboutir le bouton **Approve**.

---

## 3. qms_core — Socle (standards, exigences, processus, risques, contrôles, preuves)

**Rôle :** le référentiel commun vers lequel pointent tous les autres modules. Préfixe : `qms.*`.

### 3.1 Standards (`qms.standard`) — QMS System → Management System → Standards

Champs clés : `code` (unique par société + version), `version`, `edition`,
`standard_family` (quality / environment / ohs / food_safety / audit / measurement /
customer / other), `is_certifiable`, `issuing_body`, `lifecycle_status`, `supersedes_id`,
`transition_due_date`.

`lifecycle_status` : **Draft → Current → Superseded / Withdrawn** (Brouillon → En vigueur →
Remplacé / Retiré).

| Bouton / action | Effet |
|-----------------|-------|
| `action_activate` | `active=True`, statut → Current |
| `action_set_current` | statut → Current (l'enregistrement doit être actif) |
| `action_supersede` | statut → Superseded, archivé |
| `action_archive` | archivé (`active=False`) |

**Astuce :** conservez une seule version **Current** par famille de standard et par société ;
liez l'ancienne édition via `supersedes_id` et planifiez la migration avec une Transition
de standard (voir ci-dessous).

### 3.2 Articles (`qms.standard.clause`)

Arborescence par standard (`code` unique dans le standard, `parent_id` dans le même standard).
Construisez d'abord l'arborescence (ex. chapitres 4–10), puis rattachez les exigences à
l'article le plus fin.

### 3.3 Exigences (`qms.requirement`) — l'épine dorsale de la conformité

Champs clés : `code` (séquence auto `qms.requirement`), `standard_id`, `clause_id`,
`implementation_status`, `compliance_state` calculé, liens vers processus/risques/contrôles/preuves.

`implementation_status` : **Not Assessed / Planned / Implemented / Partially Implemented /
Not Applicable** (Non évalué / Planifié / Mis en œuvre / Partiellement mis en œuvre / Non applicable).
`compliance_state` (calculé, utilisé par le Dashboard et la Revue de direction) :
**Missing Evidence / Partially Supported / Supported** (Preuve manquante / Partiellement étayé / Étayé).

Boutons de workflow :

- `action_mark_supported` — exige **au moins une preuve Valid**, passe à Implemented +
  `assessment_date` + `assessed_by_id`.
- `action_assess_partial` — passe à Partially Implemented.
- `action_mark_not_applicable` — passe à Not Applicable (compté comme Supported dans la matrice).

**Pas à pas :** 1) créez l'exigence sur le bon article, 2) liez processus/risques/contrôles,
3) joignez la preuve et **Validez**-la (voir 3.6), 4) cliquez **Mark Supported**.
**Astuce :** le forage `action_open_missing_requirements` du Dashboard liste exactement les
exigences en `missing`/`partial` — votre liste de tâches quotidienne.

### 3.4 Processus (`qms.process`)

Champs : `code`, `owner_id` (**Process Owner**), `input_description`, `output_description`,
`objective`. Compteurs `requirement_count / risk_count / control_count`.
Pas de workflow — tenez à jour le pilote et la description Entrées/Sorties ; audits et NCR
s'y rattachent.

### 3.5 Risques (`qms.risk`)

Champs : `likelihood` / `impact` / `residual_likelihood` / `residual_impact` (entiers **1–5**),
`inherent_score = likelihood × impact` et `residual_score` calculés, niveaux
**Low (<5) / Medium (≥5) / High (≥12) / Critical (≥20)**.
`state` : **Identified → Assessed → Treatment Planned → Accepted** (Identifié → Évalué →
Traitement planifié → Accepté). Liez les `control_ids` en guise de traitement.

**Astuce :** le Dashboard et le snapshot de revue de direction comptent les risques dont le
`residual_level` est High/Critical — renseignez toujours la cotation *résiduelle* après contrôles.

### 3.6 Contrôles (`qms.control`) & Preuves (`qms.evidence`)

Contrôle : `control_type` (**Preventive / Detective / Corrective**),
`frequency` (**Per Event / Daily / Weekly / Monthly / Quarterly / Annual**),
`owner_id` (Control Owner).

Preuve : `evidence_type` (Document, Photo, Record, Training, Inspection, Measurement,
Certificate, Meeting Record, System Record, Other), `evidence_date`, `valid_from`/`valid_until`,
`status` : **Draft → Valid → Expired / Rejected**.

| Bouton | Signification |
|--------|---------------|
| `action_validate` | calcule le `integrity_hash` SHA-256 des pièces jointes, statut → Valid |
| `action_reject` | statut → Rejected |
| `action_expire` | statut → Expired (aussi automatique via cron `_cron_expire_records` quand `valid_until` est dépassée) |

**Astuce :** renseignez `valid_until` sur les preuves à durée limitée (certificats,
attestations) — l'expiration déclasse automatiquement les exigences liées vers Partial/Missing.

### 3.7 Transitions de standards (`qms.standard.transition` + `qms.standard.mapping`)

Pour migrer ex. ISO 9001:2015 → édition 2026. Champs de correspondance : `mapping_type`
(Equivalent / Changed / New / Removed / Merged / Split), `impact`, `status`
(**Open / Assessed / Migrated / Not Applicable**).
État de transition : **Planned → Assessing → In Progress → Completed / Cancelled** via
`action_start_assessment`, `action_start`, `action_complete` (bloqué tant qu'une
correspondance n'est pas Migrated/Not Applicable), `action_cancel`.
Progression = `completion_percent`.

---

## 4. qms_context — Contexte, parties intéressées, périmètre, obligations, opportunités

Menu : QMS System → Management System → **Context & Compliance**. Tous les modèles portent `company_id`.

### 4.1 Enjeux de contexte (`qms.context.issue`)

`issue_type` : **Internal / External** ; `category` : Strategic, Customer, Technology, People,
Regulatory, Supply Chain, Environment, Health & Safety, Financial, Other.
`status` : **Open → In Progress → Resolved → Closed**. Champ `climate_relevance`
(Not Assessed / Not Relevant / Relevant / Material) couvrant l'amendement climatique ISO.
Suivi via `review_date` et `owner_id`.

### 4.2 Parties intéressées (`qms.interested.party`)

`category` : Customer, Employee/Worker, Supplier, Regulator, Owner/Investor, Community,
Business Partner, Other. Champs clés : `needs_expectations` (obligatoire), `requirements`,
`monitoring_method`, `relevant`, `review_date`.

### 4.3 Périmètre (`qms.management.scope`)

Idéalement un périmètre approuvé par société. Champs : `scope_text` (obligatoire), `sites`,
`products_services`, `processes`, `exclusions`, `effective_date`, `review_date`.
`state` : **Draft → Approved → Superseded** via `action_approve` / `action_supersede`.

### 4.4 Obligations de conformité (`qms.compliance.obligation`)

`code` auto-séquencé ; `obligation_type` : Legal/Regulatory, Contractual, Customer Requirement,
Industry/Voluntary, Internal Commitment. `status` : **Identified / Applicable / Not Applicable /
Under Review / Compliant / Gap Identified**. `review_date` obligatoire + `next_review_date`
(contrainte : suivante ≥ en cours). Liens `applicable_process_ids` et `evidence_ids`.

**Workflow :** Identified → Applicable → (Under Review) → Compliant, ou → Gap Identified
(qui doit générer une NCR ou une amélioration).

### 4.5 Opportunités (`qms.opportunity`)

`source` : Audit, Risk Review, Complaint, Objective, Employee Suggestion, Management Review, Other.
`priority` : Low / Normal / High / Strategic. `status` :
**Identified → Approved → In Progress → Completed / Rejected** via `action_approve`,
`action_start`, `action_complete` (**exige `result`**), `action_reject`.

**Astuce :** les opportunités alimentent le snapshot de revue (`open_opportunity_count`) —
clôturez ou rejetez les opportunités périmées avant `action_prepare_snapshot`.

---

## 5. qms_documents — Documents contrôlés

Menu : QMS System → **Documents**. Modèles : `qms.document`, `qms.document.version`, `qms.document.ack`.

### Workflow (le cœur du module)

État du document : **Draft → Under Review → Pending Approval → Published → Obsolete**
(Brouillon → En revue → En attente d'approbation → Publié → Obsolète).

1. **Créez** le document (`code` auto-séquencé, `document_type` : Policy / Procedure /
   Work Instruction / Form-Template / Manual / Record / Other, `owner_id`).
2. **Nouvelle version** — `action_create_version` crée une `qms.document.version`
   (`revision`, `prepared_by_id` = vous, `content_note`, fichiers via `attachment_ids`).
   Renseignez `reviewer_id` sur la version (doit différer du préparateur — contrôlé).
3. **Soumettre en revue** — `action_submit_review` (brouillon uniquement, version en cours exigée).
4. **Demander l'approbation** — `action_request_approval` (en revue uniquement).
5. **Approuver** — `action_approve` : uniquement le vérificateur assigné, jamais le préparateur ;
   horodate `approved_by_id` + `approval_date`, version → Approved.
6. **Publier** — `action_publish` : exige la version Approved ; renseigne
   `publication_date`, version → Published.
7. **Rendre obsolète** — `action_obsolete` (désactive aussi l'enregistrement).

Champs de liaison : `requirement_ids`, `process_ids`, `review_date` (alimente
`overdue_document_review_count` du Dashboard), `current_version_id` / `version_ids`.

### Accusés de lecture (`qms.document.ack`)

Après publication, créez une ligne par employé (`employee_user_id`, `version_id`).
`status` : **Pending → Acknowledged** via `action_acknowledge` (uniquement l'employé assigné
ou un QMS Manager ; horodate `acknowledged_on`).

**Astuces :** ne modifiez jamais un document Published en place — créez une nouvelle révision ;
renseignez `review_date` sur chaque document publié pour que les revues en retard remontent
au cockpit.

---

## 6. qms_training — Formations, affectations, compétences

Menu : QMS Progress → **People & Competence**.

### 6.1 Formations (`qms.training.course`)

Champs : `code`, `course_type` (Induction / Procedure / Quality / Safety / Compliance /
Technical / Other), `validity_days` (défaut 365, jamais négatif), liens vers
`requirement_ids` et `document_ids` (formez sur la version contrôlée du document !).

### 6.2 Affectations (`qms.training.assignment`) — le workflow quotidien

`state` : **Assigned → Completed → Expired** (ou **Cancelled**).

1. Créez l'affectation (`course_id`, `employee_id` = res.users, `assigned_date`, `due_date`,
   `minimum_score`, preuves `evidence_ids` type certificats).
2. Saisissez `score` (0–100) et `completed_date`.
3. **Mark Completed** — `action_mark_completed` : refuse les scores sous `minimum_score` ;
   calcule `expiry_date = completed_date + validity_days`.
4. Le cron `_cron_mark_expired` fait passer à **Expired** les affectations terminées dont
   `expiry_date < today` (elles comptent alors dans `training_gap_count` du Dashboard).
5. `action_cancel` à tout moment.

Contrainte : unicité employé + formation + `assigned_date` ; scores entre 0 et 100.

### 6.3 Compétences (`qms.competency.requirement` + `qms.employee.competency`)

Exigence : `role_name`, `level` (**Awareness / Basic / Working / Advanced / Expert**),
`process_ids` liés et `course_ids` requis.
Fiche employé : `achieved_level`, `assessment_date`, `expiry_date`, `evidence_ids`,
`status` : **Provisional / Qualified / Expired / Not Met**.

**Astuce :** le module audit contrôle ces fiches — un audit avec `required_competency_ids`
ne peut démarrer si l'auditeur principal n'est pas **Qualified**
(`auditor_competence_status = Gap` bloque `action_start`).

---

## 7. qms_audit — Programmes, modèles, audits, constats

Menu : QMS Assurance → **Audit Programmes / Audits / Audit Findings**.

### 7.1 Programme (`qms.audit.program`)

Conteneur annuel (ou Quarterly/Monthly/Ad Hoc via `cycle_type`) : `year`, `objective`,
drapeau `risk_based` + `risk_review_date`, `owner_id`. Calculés : `audit_count`,
`closed_audit_count`, `completion_rate`.

### 7.2 Modèles (`qms.audit.template` + lignes)

Check-lists réutilisables : `standard_id` + lignes (`question` obligatoire, `requirement_id`,
`criterion`, `method` : Document Review / Interview / Observation / Sampling / System Record).
Le bouton **`action_create_audit`** génère un `qms.audit` avec ses lignes `qms.audit.line`.

### 7.3 Audit (`qms.audit`) — workflow principal

État : **Planned → Scheduled → In Progress → Report → Closed**
(Planifié → Planifié-daté → En cours → Rapport → Clôturé).

| Étape | Bouton | Gardes |
|-------|--------|--------|
| Planifier | (création) | `audit_type` (Internal/Supplier/Customer/Certification/Surveillance/Regulatory/Process/Product), `scope` (obligatoire), `lead_auditor_id`, `program_id` |
| Programmer | `action_schedule` | — |
| Démarrer | `action_start` | audits risk-based : `risk_basis` obligatoire ; auditeur principal ≠ `auditee_owner_id` (indépendance) ; pas d'écart de compétence ; ≥ 1 ligne de contrôle |
| Exécuter | (renseigner lignes) | chaque `qms.audit.line` : `result` = Conform / Observation / Minor NC / Major NC / Not Applicable + `evidence_ids` |
| Rapporter | `action_generate_report` | chaque ligne doit avoir un `result` |
| Clôturer | `action_close` | état Report exigé ; chaque ligne doit avoir un résultat ; horodate `end_date` |

Statistiques live : `line_count`, `conform_count`, `compliance_rate`. Cases
`opening_meeting_done` / `closing_meeting_done` pour les réunions d'ouverture/clôture.

### 7.4 Constats (`qms.finding`)

Créés depuis les contrôles en écart : `severity` (**Observation / Minor / Major**),
`description`, `requirement_id`, `evidence_ids`, `audit_line_id`.
État : **Open → Converted to NCR / Closed**. Le bouton **`action_create_ncr`** (ajouté par
`qms_ncr_capa`) crée la NCR avec sévérité transposée (observation→minor, minor→major,
major→critical) et fait passer le constat à Converted.

**Astuce :** ne clôturez jamais un audit avec des lignes vides — le garde-fou exige un
résultat sur chaque contrôle, ce que le certificateur vérifiera.

---

## 8. qms_certification — Certificats & surveillance

Menu : QMS Assurance → **Certification**. Modèle `qms.certification`.

Champs clés : `code`, `standard_id` (obligatoire), `certification_body_id` (partenaire),
`certificate_number` (unique par société, obligatoire), `scope` (obligatoire),
`issue_date`, `expiry_date`, `audit_ids` liés (audits de certification/surveillance),
`attachment_ids` (scan du certificat).

`status` : **Draft → Active → Expiring → Expired** (plus **Suspended**, **Renewed**).

- `action_activate` — exige les deux dates ; → Active.
- `action_suspend` — → Suspended (ex. après un constat majeur).
- `action_mark_renewed` — → Renewed (créez le nouveau certificat, puis marquez l'ancien).
- Cron nocturne `_cron_update_status` : **Expired** si `expiry_date < today` ;
  **Expiring** si expiration sous **90 jours** (`threshold = today + 90`).

**Astuce :** rattachez les audits de surveillance/certification via `audit_ids` — le compteur
`audit_count` documente votre piste d'audit pour l'organisme certificateur.

---

## 9. qms_ncr_capa — Non-conformités, CAPA, Coût qualité

Menu : QMS Assurance → **Non-Conformities / CAPA / Cost of Quality**.

### 9.1 NCR (`qms.ncr`) — le workflow verrouillé en 6 étapes

Statut : **New → Containment → Root Cause Analysis → Action Plan → Effectiveness → Closed**
(Nouveau → Confinement → Analyse des causes → Plan d'actions → Efficacité → Clôturé).

| Étape | Bouton | Garde |
|-------|--------|-------|
| 1. Enregistrer | (création) | `source` (Audit/Complaint/Supplier/Process/Inspection/Other), `severity` (Minor/Major/Critical), `description` (obligatoire), liens `audit_id`/`finding_id`/`requirement_id`/`process_id`, `root_cause_method` (5 Whys / Ishikawa / 8D / A3 / Custom) |
| 2. Confiner | `action_start_containment` | depuis New uniquement |
| 3. Analyser | `action_start_analysis` | depuis Containment + texte `containment` exigé |
| 4. Planifier | `action_open_action_plan` | depuis Analysis + `root_cause` exigé |
| 5. Vérifier | `action_verify_effectiveness` | depuis Action Plan + ≥ 1 CAPA, toutes `implemented`/`effective` |
| 6. Clôturer | `action_close` | chaque CAPA doit être `effective` (`all_capa_effective`) ; le constat lié → Converted |

### 9.2 CAPA (`qms.capa`)

Champs : `action_type` (**Corrective / Preventive / Correction**), `action_description`,
`owner_id`, `deadline`, `implementation_date`, `verification_date`, `verification_method`,
`effectiveness_note`, `evidence_ids`.
Statut : **Planned → In Progress → Implemented → Effective** (ou Ineffective/Cancelled).

- `action_start` → In Progress.
- `action_mark_implemented` — exige `implementation_date`.
- `action_mark_effective` — exige `verification_date` + `verification_method`.
- `action_mark_ineffective` — → Ineffective **et renvoie la NCR parente en Action Plan**
  (re-planifiez une nouvelle action).

### 9.3 Coût qualité (`qms.quality.cost`)

Chaque ligne : `date`, `cost_type` (**Prevention / Appraisal / Internal Failure /
External Failure**), `amount` (monétaire, jamais négatif), liens optionnels `ncr_id` / `capa_id`.
Le Dashboard totalise les lignes dans `cost_of_quality` par société.

**Astuce :** renseignez toujours une `deadline` CAPA — le Dashboard et la Revue de direction
comptent `deadline < today ET statut ∉ (Effective, Cancelled)` comme **CAPA en retard**.

---

## 10. qms_complaints — Réclamations clients (SLA + portail)

Menu : QMS Assurance → **Customer Complaints**. Modèle `qms.complaint`
(hérite de `portal.mixin` — partage portail inclus).

### Workflow

État : **New → Acknowledged → Investigating → Waiting for Customer → Resolved → Closed**
(Nouveau → Accusé → En enquête → En attente client → Résolu → Clôturé) ou **Cancelled**.

1. **Créez** (ou via le formulaire portail) : `partner_id` (obligatoire), `category`
   (Product/Service/Delivery/Documentation/Communication/Other), `priority`
   (Low/Normal/High/Critical), `description`, `assigned_to_id`.
2. `action_acknowledge` → Acknowledged (surveillez le délai d'accusé !).
3. `action_investigate` → Investigating ; `action_wait_customer` si une entrée client manque.
4. `action_resolve` — **exige le texte `resolution`** → Resolved.
5. `action_close` — uniquement depuis Resolved ; horodate `closed_at`. Optionnel : `satisfaction_score`.
6. `action_escalate_to_ncr` — crée une NCR liée (`source=Complaint`, sévérité Major si
   priorité High/Critical sinon Minor), stockée dans `ncr_id`.

### Champs SLA (le cœur du module)

- `response_sla_hours` (défaut **24.0**), `sla_deadline` = `received_at + response_sla_hours`.
- `sla_escalation_hours` (défaut **4.0**), `acknowledgement_deadline` = `received_at + escalation`.
- `sla_breached` (calculé : délai dépassé alors que non Resolved/Closed/Cancelled).
- Cron nocturne `_cron_sla_breach` : horodate `escalated_at` et crée une activité
  **« Complaint SLA breached »** pour l'assigné (une seule fois).

### Portail

Templates `portal_my_complaints` / `portal_new_complaint` : le client voit
Référence (`code`), Objet, Statut, Date de réception et SLA sur `/my/qms-complaints`,
peut déposer une réclamation (`/my/qms-complaints/new`) et ouvrir chaque fiche
(`/my/qms-complaints/<id>`). Aucune configuration portail au-delà de l'accès portail Odoo standard.

**Astuce :** gardez `response_sla_hours > sla_escalation_hours` ; l'activité d'escalade est
votre alerte précoce avant le dépassement contractuel.

---

## 11. qms_supplier — Qualification, évaluations, certificats

Menu : QMS Assurance → **Suppliers** (Profiles / Certificates / Evaluations).

### 11.1 Profil (`qms.supplier`)

Un profil par partenaire et par société (`partner_company_uniq`). Champs : `partner_id`,
`risk_level` (Low/Medium/High/Critical), `owner_id`, `review_date`.
`qualification_status` : **Draft → Qualified** (via `action_qualify`), **↔ Suspended**
(`action_suspend`), re-qualifiez avec `action_requalify`. (`probation` et `disqualified`
découlent des évaluations — voir ci-dessous.)

### 11.2 Certificats (`qms.supplier.certificate`)

`certificate_number`, `issuing_body_id`, `standard_id`, `issue_date`, `expiry_date`,
`status` : **Draft → Active → Expiring → Expired** (ou Superseded).
Cron `_cron_update_status` avec seuil d'alerte **60 jours** (contre 90 jours pour les
certificats QMS).

### 11.3 Évaluations (`qms.supplier.evaluation`)

Un enregistrement par campagne : `evaluation_date`, `evaluator_id`, quatre notes 0–100
(`quality_score`, `delivery_score`, `responsiveness_score`, `compliance_score`),
`overall_score` calculé (moyenne), `conclusion` : **Approved / Conditional /
Improvement Required**. Le profil affiche `latest_score` + `latest_evaluation_date`.

**Pas à pas :** 1) créez le profil (Draft), 2) enregistrez les certificats,
3) réalisez une évaluation, 4) `action_qualify` (ou Suspend), 5) planifiez la réévaluation
via `review_date`.
**Astuce :** une évaluation *Improvement Required* devrait générer une NCR source Supplier.

---

## 12. qms_measurement — Équipements & étalonnage

Menu : QMS Assurance → **Measurement & Calibration** (Equipment / Calibration Records).

### 12.1 Équipements (`qms.measurement.equipment`)

Champs : `code` (auto-séquencé), `equipment_type`, `manufacturer`, `serial_number`, `location`,
`measurement_range`, `accuracy`, `tolerance`, `required_uncertainty`,
`traceability_reference`, `calibration_provider`, `criticality` (Low/Medium/High),
`calibration_interval` (jours, défaut 365, > 0 obligatoire), `last_calibration_date`,
`next_due_date` calculé = dernier + intervalle, liens `process_ids` / `control_ids`.

État : **Draft → Active → Due (aujourd'hui) → Overdue** (ou **Out of Service**).
Le cron `_cron_update_status` fait passer Active → Overdue après l'échéance.
Boutons : `action_activate`, `action_out_of_service`.

### 12.2 Étalonnages (`qms.measurement.calibration`)

Champs : `calibration_date`, `performed_by_id`, `certificate_number`, `reference_standard`,
`measurement_uncertainty`, `decision_rule`, `environmental_conditions`,
`result` : **Pass / Conditional Pass / Fail**, `as_found` / `as_left` : Pass / Fail / Unknown,
`impact_review`, `attachment_ids`.

Bouton **`action_validate`** :

- `result = Fail` → équipement → **Out of Service** (renseignez `impact_review` ! — quels lots
  mesurés avec cet appareil sont suspects ?).
- sinon → recalcule `next_due_date`, renseigne `last_calibration_date`, équipement → Active.

**Astuce :** un étalonnage en échec avec `as_found = Fail` signifie que les mesures passées
sont suspectes — documentez la revue d'impact et envisagez une NCR source Inspection.

---

## 13. qms_objectives — Objectifs qualité

Menu : QMS Progress → **Performance** (Objectives / Measurements). Modèle `qms.objective`.

Champs clés : `code`, `objective_type` (Quality/Customer/Process/Supplier/Compliance/People/Other),
`process_id`, `owner_id`, `direction` (**Increase / Decrease / Reach Target**),
`unit`, `baseline_value`, `target_value`, `current_value` calculé (dernière mesure),
`progress_percent` calculé (0–100), `start_date`/`deadline`, `measurement_count`.
Statut : **Draft → On Track → At Risk → Delayed → Achieved / Failed** (ou Cancelled) via
`action_set_on_track`, `action_set_at_risk`, `action_set_delayed`,
`action_mark_achieved`, `action_mark_failed`, `action_cancel`.

Mesures (`qms.objective.measurement`) : `date`, `value`, `source`, `note`.
Chaque nouvelle mesure recalcule `current_value` et `progress_percent`.

**Pas à pas :** 1) créez l'objectif avec baseline + cible + direction,
2) passez On Track, 3) saisissez les mesures périodiques, 4) basculez At Risk/Delayed en cas
de dérive (le Dashboard compte exactement ces deux-là dans `objectives_at_risk_count`),
5) marquez Achieved/Failed à l'échéance.
**Astuce :** choisissez une `unit` et tenez-vous-y (%, ppm, jours…) — des unités mélangées
dans les mesures faussent silencieusement la courbe de progression.

---

## 14. qms_improvement — Kaizen & leçons apprises

Menu : QMS Progress → **Continuous Improvement** (Improvements / Lessons Learned).

### 14.1 Améliorations (`qms.improvement`)

Champs : `code`, `improvement_type` (Kaizen / Process / Cost Reduction / Customer Experience /
Quality / Other), `source` (Audit / NCR-CAPA / Complaint / Risk Review / Objective /
Suggestion / Other), `description`, `owner_id`, `target_date`, `priority`
(Low/Normal/High/Strategic), `baseline_value`/`target_value`/`actual_value` + `unit`,
`expected_benefit`, `benefit_value` (monétaire), `action_plan`, `lessons_learned`.

Statut : **Idea → Approved → In Progress → Completed → Standardized** (ou Cancelled) :

- `action_approve`, `action_start`,
- `action_complete` — **exige `lessons_learned`**,
- `action_standardize` — uniquement depuis Completed (mettez à jour ici le document
  contrôlé / le contrôle !),
- `action_cancel`.

### 14.2 Leçons apprises (`qms.lesson.learned`)

`date`, `situation`, `learning` (tous deux obligatoires), `action_to_standardize`, `owner_id`,
drapeau `shared`, statut : **Draft → Approved → Shared → Archived**.

**Astuce :** l'étape Standardized est la raison d'être du module — sans elle, les
améliorations s'évaporent. Liez le document ou le contrôle mis à jour dans
`action_to_standardize`.

---

## 15. qms_management_review — Revues & actions (+ snapshot expliqué)

Menu : QMS Cockpit → **Management Review** (Reviews / Actions).

### Revue (`qms.management.review`)

Champs : `code`, `meeting_date`, `period_start`/`period_end`, `chair_id`, `attendee_ids` ;
compteurs figés (voir ci-dessous) ; synthèses modifiables (`audit_summary`, `ncr_capa_summary`,
`risk_summary`, `objective_summary`, `people_summary`, `context_summary`,
`supplier_summary`, `measurement_summary`, `improvement_summary`, `resource_needs`, `decisions`) ;
`action_ids` (suivis responsabilisés).

État : **Draft → Prepared → Held → Closed** (Brouillon → Préparée → Tenue → Clôturée).

1. **Préparer** — `action_prepare_snapshot` : fige une photo à date sur
   `[period_start, period_end]` (par défaut les 365 jours avant `meeting_date`) :
   - `closed_audit_count` — audits clôturés sur la période ;
   - `open_ncr_count` — NCR non clôturées ;
   - `overdue_capa_count` — CAPA avec `deadline < period_end`, statut ∉ (Effective, Cancelled) ;
   - `high_risk_count` — résiduel High/Critical ;
   - `objective_at_risk_count` — At Risk/Delayed ;
   - `expired_training_count` — affectations Expired ;
   - `open_complaint_count` — réclamations ∉ (Closed, Cancelled) ;
   - `overdue_calibration_count` — équipements Overdue ;
   - `open_opportunity_count` — opportunités ∉ (Completed, Rejected) ;
   - `compliance_gap_count` — exigences en Missing evidence ;
   plus une phrase de synthèse auto-générée par domaine (modifiable ensuite).
2. **Tenir** — `action_mark_held` (exige Prepared) : consignez `decisions` + `resource_needs`,
   créez les lignes `qms.management.action` (nom, `owner_id`, `due_date`, `description`).
3. **Clôturer** — `action_close` (exige Held **et** chaque action `done`/`cancelled`).

### Actions (`qms.management.action`)

Statut : **Planned → In Progress → Done** (ou Cancelled) via `action_start`,
`action_done`, `action_cancel`.

**Astuce :** le snapshot est figé — les modifications ultérieures des NCR/audits ne
réécrivent pas l'historique. Ne relancez `action_prepare_snapshot` qu'*avant* la réunion si
la période change ; après Held, les chiffres sont votre preuve d'audit.

---

## 16. qms_dashboard — Cockpit OWL, KPIs, indice de préparation

Menu : QMS Cockpit → **Dashboard** (+ **Compliance → Compliance Matrix**).
Un enregistrement `qms.dashboard` par société (`company_uniq`), actualisé via `action_refresh`
ou le cron hebdomadaire `_cron_weekly_digest` (digest e-mail aux QMS Managers).

### Ce que vous voyez (application OWL `qms_cockpit.js`)

`get_dashboard_data()` retourne :

- **KPIs :** NCR ouvertes, CAPA en retard, audits ouverts, couverture des exigences %,
  réclamations ouvertes, écarts de formation, étalonnages en retard, risques élevés.
- **Graphiques :** donut de couverture (Supported/Partial/Missing), barres NCR par statut
  (New/Containment/Analysis/Action Plan/Effectiveness/Closed), tendance 6 mois NCR/audits,
  réclamations par état.
- Cliquez sur un KPI pour forer (`action_open_ncr`, `action_open_capa`, `action_open_risks`,
  `action_open_training`, `action_open_audits`, `action_open_complaints`,
  `action_open_calibration`, `action_open_improvements`, `action_open_missing_requirements`).

### Indice de préparation (le chiffre principal)

Indicateur de gestion pondéré (PAS un score de certification — voir `methodology_note`) :

| Composante | Poids | Logique |
|-----------|-------|---------|
| Couverture des exigences (`supported/total`) | 30 % | d'après `compliance_state` |
| Validité des preuves | 12 % | preuves valides / total |
| NCR majeures ouvertes | 12 % | −10 pts par NCR Major/Critical ouverte |
| CAPA en retard | 12 % | −12,5 pts par CAPA en retard |
| Exposition résiduelle aux risques | 10 % | −8 pts par risque High/Critical |
| Écarts de formation | 8 % | −5 pts par écart expired/assigned |
| Dépassements SLA réclamations | 8 % | −10 pts par réclamation en dépassement |
| Étalonnages en retard | 8 % | −8 pts par appareil en retard |

`readiness_band` : **Strong (≥ 85) / Needs Attention (≥ 70) / Priority Gaps (< 70)**
(Solide / Vigilance requise / Écarts prioritaires).

**Comment faire progresser l'indice :** validez les preuves + marquez les exigences Supported
(30 %), clôturez les NCR majeures, terminez les CAPA en retard, reformez les affectations
expirées, étalonnez les appareils en retard, traitez les réclamations en dépassement.
Relancez **Refresh** (`action_refresh`) après chaque lot.

La **Compliance Matrix** (`qms.requirement` groupé par standard/article avec couleurs
`compliance_state`) est le jumeau « auditeur » des mêmes données.

---

## 17. FAQ

### 1. La suite est-elle multi-sociétés ?

Oui. Chaque modèle opérationnel porte `company_id` (défaut : société courante) avec
`check_company=True` sur les relations et des codes uniques par société
(`code_company_uniq` / `partner_company_uniq`). Séquences, dashboards et snapshots de revue
sont tous calculés **par société**. Changez de société dans Odoo et le cockpit, la matrice
et les compteurs suivent.

### 2. Comment fonctionne l'accès portail client ?

Installez `qms_complaints` (dépend de `portal`). Les clients se connectent au portail et
ouvrent **My Quality Complaints** (`/my/qms-complaints`) : liste avec Référence/Objet/Statut/
Réception/SLA, formulaire **Submit a Complaint** (`/my/qms-complaints/new`) et page détail
par réclamation. Les champs internes (lien NCR, internes SLA) restent cantonnés au back-office.

### 3. Que se passe-t-il à l'expiration d'un certificat ?

Les certificats QMS (`qms.certification`, alerte à 90 jours) comme les certificats
fournisseurs (`qms.supplier.certificate`, alerte à 60 jours) sont balayés par les crons
nocturnes (`_cron_update_status`) : Active → **Expiring** dans la fenêtre → **Expired** après
`expiry_date`. Un certificat fournisseur expiré doit déclencher réévaluation ou suspension
(`action_suspend`) ; un certificat QMS expiré apparaît au cockpit et dans le prochain snapshot
de revue — planifiez le renouvellement via `action_mark_renewed` + un nouvel enregistrement.

### 4. Que se passe-t-il à l'expiration d'une formation ?

`validity_days` sur la formation fixe l'`expiry_date` de chaque affectation à sa complétion.
Le cron `_cron_mark_expired` les fait passer à **Expired**, où elles alimentent
`training_gap_count` (cockpit), `expired_training_count` (snapshot de revue) et peuvent dégrader
l'indice de préparation. Les compétences employés liées au cours se périment de la même façon.
Correctif : ré-affectez la formation puis **Mark Completed** à nouveau.

### 5. Que se passe-t-il en cas de dépassement SLA ?

Quand `sla_deadline` est dépassée sur une réclamation non Resolved/Closed/Cancelled,
`sla_breached` s'active et le cron `_cron_sla_breach` horodate `escalated_at` et lève une
activité **« Complaint SLA breached »** pour l'assigné. Les réclamations en dépassement
(non les simples ouvertes) pénalisent l'indice de préparation et restent listées dans
`breached_complaint_count` jusqu'à résolution. Accusez réception vite (cible d'escalade 4 h
par défaut) et résolvez avec une `resolution` documentée.

### 6. Y a-t-il des données de démonstration pour explorer ?

Oui — chaque module fournit `demo/qms_demo_*.xml` (standards, exigences, documents,
formations, programmes, audits, constats, NCR, réclamations, fournisseurs, équipements,
objectifs, améliorations, revues, certifications…). Créez une base de test **avec données
de démo**, installez **QMS Management System**, ouvrez le Cockpit et parcourez les forages
avant d'encoder votre vrai système.

---

*Manuel généré à partir des sources des modules (`__manifest__.py` + `models/*.py`) de la
suite QMS en 15 modules, Odoo 20. Les noms d'états, champs et actions sont cités verbatim (`monospace`).*
