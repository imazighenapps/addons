# QMS Management System

## Purpose
QMS Management System is the installable end-user application that assembles the complete QMS feature set into one commercial Odoo application.

It is the product-level shell. The functional logic is intentionally distributed across focused technical modules so each area can evolve independently while the customer installs one application entry point.

## Included capabilities
- QMS Core: standards, requirements, processes, risks, controls, evidence and standard transitions.
- Controlled Documents.
- Audit programs, audits, checklists and findings.
- NCR, RCA, CAPA, effectiveness and Cost of Quality.
- Training and competency.
- Quality objectives and measurements.
- Management reviews and accountable actions.
- Executive dashboard and Compliance Matrix.
- Supplier qualification and supplier evaluations.
- Certification lifecycle.
- Organizational context, interested parties and compliance obligations.
- Customer complaints and portal workflow.
- Measurement equipment and calibration management.
- Continuous improvement and lessons learned.

## Reports
The application exposes the suite-level PDF/report actions for the main operational objects, including audit, NCR/CAPA and management-review reporting.

## Commercial architecture
`qms_management` is the application entry point. The feature modules remain separated so optional Odoo bridges can be installed only when the corresponding Odoo applications are available.

## Optional Odoo bridges
- `qms_bridge_quality`: create NCRs from failed Odoo Quality checks.
- `qms_bridge_sale_purchase`: connect NCRs with Sales and Purchase orders.
- `qms_bridge_stock_mrp`: connect NCRs with stock transfers and manufacturing orders.

These bridges are deliberately outside the QMS core so Community deployments do not acquire unnecessary application dependencies.

## Supported languages
English is the source language. Translation catalogs are provided for:
- French
- Spanish
- Portuguese (Portugal)
- Portuguese (Brazil)
- German

## Dependencies
The application depends on the QMS feature modules listed in its manifest. Optional business-application integrations remain in separate bridge modules.
