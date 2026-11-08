# -*- coding: utf-8 -*-
{
    'name': 'CashRadar',
    'version': '18.0.1.0.0',
    'summary': 'Project thirteen weeks of cash from open invoices, vendor bills and recurring entries, with a delay scenario, weekly net flow and the exact week the balance turns negative.',
    'description': '''CashRadar - 13-Week Cash Forecast
=================================
The bank balance looks fine today. In six weeks three supplier bills land
on the same day, the biggest customer pays late again, and the payroll
leaves before either cheque arrives. The hole is discovered on the day it
happens, which is exactly one day too late.

CashRadar builds a rolling thirteen-week forecast from what is already in
the books: every open customer invoice is an inflow on its due date, every
open vendor bill an outflow, and the recurring entries you enter by hand -
rent, payroll, tax, subscriptions - fill in what the invoices do not show.
A delay scenario pushes the customer payments by the number of days they
usually take, so the forecast shows the real trough, not the optimistic one.
The forecast keeps the opening balance, the weekly net flow, the lowest
point and the week where the balance goes negative.

* Thirteen weeks by default, any length from one to fifty-two.
* Inflows from open customer invoices, outflows from open vendor bills.
* Recurring entries: weekly, monthly or quarterly, with a start and end.
* Delay scenario to model the customers who always pay late.
* Weekly net flow, running balance, lowest point and at-risk week.
* Opening balance per scenario, several scenarios side by side.
* Recompute on demand, no accounting entry created.
* Graph and pivot by week, multi-company isolation.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 129.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/cash_forecast_0_views.xml',
        'views/cash_forecast_line_1_views.xml',
        'views/cash_forecast_recurrence_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
