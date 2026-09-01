# EduFlow — School Management for Odoo 18

Integrated school management: students & parents, admissions, enrollments,
classes & timetables, attendance, exams & grades, report cards, fees &
payments, with role-based security and a management dashboard.

This version implements the corrections and enhancements from the
technical specification (`EduFlow_Analyse_CahierDesCharges`), organized in
6 lots:

| Lot | Content | Status |
|---|---|---|
| Lot 0 | F0.1 — blocking `hr` dependency fix | ✅ Done (`eduflow_hr_bridge`) |
| Lot 1 | F1.1-F1.4 — Accounting: invoicing, payment sync, reminders, online payment | ✅ Done |
| Lot 2 | F2.1-F2.6 — UX: attendance wizard, grade grid, kanban, calendar, search/graph/pivot, dashboard history | ✅ Done |
| Lot 3 | F3.1-F3.3 — Portal: public pre-registration, teacher space, admission documents | ✅ Done |
| Lot 4 | F4.1-F4.4 — Multi-company, settings screen, activity tracking, i18n | ✅ Done (i18n partial, see docs) |
| Lot 5 | F5.1-F5.2 — Tests & documentation | ✅ Done |

See [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) for the full functional
guide (installation, per-role walkthrough, known limitations).

## Modules

- **`eduflow`** — main module (`base`, `mail`, `portal`, `account`,
  `payment`, `website`).
- **`eduflow_hr_bridge`** — optional, auto-installs itself only when `hr`
  is present; adds the `employee_id` link on `eduflow.teacher`.

## Tests

```
odoo-bin -d <db> -i eduflow --test-enable --test-tags /eduflow --stop-after-init
```
