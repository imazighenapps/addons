# PestOps Sales Integration

Optional Community integration for Odoo 19.

## Commercial workflow

Quotation
-> Enable PestOps
-> Select service sites
-> Create PestOps Contract (draft)
-> Confirm Sales Order
-> Contract auto-confirms
-> Treatment Plans
-> Recurring Visits

## Important

- This module depends on `pestops_core` and `sale_management`.
- It does not depend on Enterprise.
- Accounting is intentionally not included.
- The contract is activated by Sales Order confirmation, not by quotation creation.
