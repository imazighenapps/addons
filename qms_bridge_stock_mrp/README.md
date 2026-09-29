# QMS Stock MRP Bridge

## Purpose
QMS Stock MRP Bridge connects operational quality issues to stock transfers and manufacturing orders.

## Main capabilities
### Stock Pickings
- Display the number of related QMS NCRs.
- Open related NCRs directly from the transfer.
- Create a QMS NCR from the transfer context.

### Manufacturing Orders
- Display the number of related QMS NCRs.
- Open related NCRs.
- Create a QMS NCR directly from the manufacturing order.

## Integration path
`Stock Transfer / Manufacturing Order → NCR → RCA → CAPA → Effectiveness`

## Menu/UI
No standalone menu. The module extends stock and manufacturing forms.

## Dependencies
`qms_ncr_capa`, `stock`, `mrp`.

## Installation behavior
Optional/automatic bridge. The QMS core remains independent of Stock and MRP.
