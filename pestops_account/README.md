# PestOps Accounting - Odoo 19 Community

V1.2 adds the financial layer without replacing Odoo Invoicing/Accounting.

## Features
- Contract billing product and payment terms.
- Recurring billing periods: one-off, monthly, quarterly, annual.
- Per-visit billing for completed visits.
- Manual/additional billing items through the Billing Items menu.
- Billing KPIs on contracts: to invoice, invoiced, invoice count.
- Batch invoice generation using native `account.move` customer invoices.
- Automatic daily preparation of billing items for confirmed contracts.
- Invoice and billing item traceability back to the PestOps contract.

## Community architecture
Dependencies: `pestops_core`, `account` only.

Odoo's native invoicing objects remain authoritative for invoices, taxes, payment terms and accounting entries. PestOps only adds the domain-specific billing layer.
