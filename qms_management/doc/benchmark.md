# QMS Management System — Benchmark Notes

This document records the product-design benchmark used during development. It is not a certification statement and does not reproduce ISO standard text.

## Reference application

The detailed public feature set used as a benchmark is the Odoo Apps Store listing for **ISO Compliance: QMS, Audits, NCR/CAPA & Document Control** by Odoo DevHouse. The publicly indexed detailed description is for Odoo 19; the current store search also surfaces the application in the Odoo ecosystem. The benchmark includes audit programs/templates, one-click NCR, 5 Whys, CAPA effectiveness, Cost of Quality, document control, risk/opportunity, objectives, supplier evaluations, customer complaints with SLA/portal, management review, equipment/calibration, dashboard, PDF reports, reminders, optional bridges and 54 automated tests.

## Design differences in this suite

- Requirement-first traceability: requirement → process → risk/opportunity → control → document → evidence → audit → finding/NCR → CAPA → effectiveness → management review.
- Standard edition lifecycle and transition mappings instead of a fixed, hard-coded clause library.
- Current-edition metadata is kept separately from copyrighted normative text. The suite can ingest customer-owned/licensed requirement datasets.
- Separate context, interested parties, management scope, compliance obligations and opportunity management.
- Explicit implementation assessment for each requirement, independent from evidence validity.
- Evidence integrity hashing and validity/expiry controls.
- Competency and training management tied to requirements and audits.
- Measurement management with traceability, uncertainty and impact review.
- Supplier qualification, supplier certificates and smart-button access from vendor contacts.
- Optional Sales/Purchase, Stock/MRP and Enterprise Quality bridges.
- Weekly QMS management digest and structured management-review inputs.
- Five-language catalogs: English source with French, Spanish, Portuguese (PT/BR) and German packs.

## Standards research used for design

The design was updated for current 2026 editions where published: ISO 9001:2026, ISO 14001:2026, ISO 19011:2026 and ISO 10012:2026. ISO 10002:2018 remains current, ISO 45001:2018 remains current with a 2024 climate amendment, and ISO 22000:2018 remains current while its revision is in progress.
