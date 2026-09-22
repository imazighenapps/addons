# PestOps Stock & Traceability — Odoo 19 Community

## Purpose

This optional module extends `pestops_core` with advanced product traceability for pest-control interventions.

## Features

- Immutable consumption ledger linked to the PestOps treatment line and Odoo stock move.
- Product, lot/serial, quantity, site, zone, visit, technician and source-location traceability.
- Pre-consumption stock validation.
- Required lot/serial enforcement when product tracking is enabled.
- Expired lot prevention.
- Live available quantity and stock status on treatment consumption lines.
- Configurable minimum-stock threshold per product and internal location.
- Automatic daily low-stock activities for the responsible user.
- List and pivot analysis of historical consumption.

## Dependency model

`pestops_stock` depends only on `pestops_core` and `stock`. It does not require Odoo Enterprise.

## Notes

The trace ledger is intentionally read-only from the UI. Trace records are created by the consumption workflow after the corresponding stock move is completed.
