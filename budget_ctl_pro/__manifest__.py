# -*- coding: utf-8 -*-
{
    'name': 'BudgetCtlPro',
    'version': '18.0.1.0.0',
    'summary': 'Compare planned, actual and committed amounts line by line, see what is really left to spend, and freeze the budget once the period is closed.',
    'description': '''BudgetCtlPro - Budget Control with Commitments
==============================================
Every finance team knows the spreadsheet: one column for the budget, one
for the invoices already received, and a third one that nobody updates for
the purchase orders signed last week. The budget looks fine until those
orders are invoiced and the department is suddenly over its envelope. The
missing piece is the commitment: money already engaged, not yet spent.

BudgetCtlPro puts the three amounts on the same line. Each budget covers a
period and, optionally, one analytic account; leave the analytic account
empty and the budget simply covers the whole company, which keeps the
module usable on a fresh database without any analytic plan. Every budget
line carries a planned amount, the actual amount already invoiced and the
committed amount still engaged, and the available amount is recomputed as
planned minus actual minus committed. The budget header sums its lines and
raises an overspend flag as soon as the available amount turns negative.
Start a budget when the period opens, close it when the period ends and the
lines are locked for good, then reset it to draft if a correction is
needed. Codes come from a BGT/ sequence, totals are stored for fast
reporting, and every action is traced in the chatter. The module is
multi-company, multi-currency and works on Community as well as Enterprise.

* Planned, actual and committed amounts on every budget line.
* Available amount recomputed as planned minus actual minus committed.
* Stored header totals and an automatic overspend flag.
* Optional analytic account, or a global budget for the whole company.
* Period based budgets with a BGT/ sequence for the reference.
* Draft, running and closed states with a full audit trail.
* Budget lines locked once the budget is closed, unlocked by a reset.
* Multi-company, multi-currency, no Enterprise dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 129.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'account',
        'analytic',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/budgetctl_budget_0_views.xml',
        'views/budgetctl_budget_line_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
