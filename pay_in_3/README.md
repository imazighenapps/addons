# PayIn3

Invoice Payment Plans

## The problem

A customer pays in three times, but Odoo keeps one invoice and one balance: the follow-up lives in a note, the second and third installments are chased by hand, and the balance is wrong as soon as one transfer is late.

## The solution

Split a customer invoice into two, three or four dated installments, track what is paid, and register the payment of each installment without leaving the invoice.

## Main features

- Split an invoice into dated installments.
- Two, three, four installments or any count.
- Sum equal to the total, rounding on the last one.
- Paid and remaining amounts on the plan.
- Payment wizard pre-filled for each installment.
- Draft, active, done and cancelled states.
- Safe recompute while nothing is paid.
- Kanban, graph and pivot, multi-company isolation.

## Installation

1. Install the module from the Apps list.
2. Open the **Payment Plans** menu.
3. Create your first record and follow the guided empty state.

## Compatibility

- Odoo 18.0 Community and Enterprise.
- Odoo 19.0 and 20.0 versions are provided separately.
- No external Python dependency.

## License

OPL-1 (Odoo Proprietary License).
