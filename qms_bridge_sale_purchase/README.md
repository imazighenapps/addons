# QMS Sales Purchase Bridge

## Purpose
QMS Sales Purchase Bridge connects non-conformities with Odoo Sales and Purchase documents so quality issues can be traced to commercial transactions and supplier-related purchasing records.

## Main capabilities
### Sales Orders
- Display a QMS NCR count on the Sales Order.
- Open linked QMS NCRs from the Sales Order.
- Create a QMS NCR directly from the Sales Order.

### Purchase Orders
- Display a QMS NCR count on the Purchase Order.
- Open linked QMS NCRs from the Purchase Order.
- Create a QMS NCR directly from the Purchase Order.

## Integration path
`Sales/Purchase Document → NCR → RCA → CAPA → Effectiveness`

## Menu/UI
No standalone QMS menu. The bridge extends Sales and Purchase forms.

## Dependencies
`qms_ncr_capa`, `sale`, `purchase`.

## Installation behavior
Optional/automatic bridge. It does not force Sales or Purchase dependencies into the QMS core application.
