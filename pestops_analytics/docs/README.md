# PestOps Analytics & Business Intelligence — V2.0

PestOps Analytics adds read-only management reporting on top of the PestOps Community suite.

## Reports
- Executive KPIs by company.
- Visit analytics (graph, pivot, list).
- Site performance KPIs.
- Technician performance KPIs.
- Contract portfolio KPIs.
- Financial/billing analytics (graph, pivot, list).

## Design principles
- Read-only SQL views; no duplicate transactional data.
- Odoo Community modules remain the source of truth.
- No Enterprise dependency.
- Metrics are factual aggregates; no ranking logic is embedded in the module.

## Main KPIs
- operational activity and overdue work;
- anomalies, re-services and quality issues;
- stock consumption and threshold alerts;
- equipment due actions and maintenance cost;
- contract portfolio and billing status;
- invoice/billing evolution over time.
