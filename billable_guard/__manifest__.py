# -*- coding: utf-8 -*-
{
    'name': 'BillableGuard',
    'version': '18.0.1.0.0',
    'summary': 'Compare logged timesheets with what has actually been invoiced, flag every unbilled hour with its amount at risk and prepare the invoice in one click.',
    'description': '''BillableGuard - Unbilled Time Alerts
====================================
An agency bills by the hour. The team logs its time, the project advances,
the customer is happy, and at the end of the quarter somebody notices that
two hundred hours were never invoiced. The work was done, the cost was
paid, and the revenue simply vanished.

BillableGuard reads the timesheets of a period and compares them with what
the linked sales order has already delivered and invoiced. Every group of
hours that is no longer invoiced becomes a gap, with the hours logged, the
hours invoiced, the difference and the amount at risk at the sales price.
The scan never creates the same gap twice, and the project carries a risk
level so the manager sees the problem before the closing meeting. One click
opens the standard invoice wizard for the sales order behind the gap.

* Unbilled hours detected from real timesheets, per project and employee.
* Hours logged, hours invoiced and the gap, side by side.
* Amount at risk computed at the sales order price.
* Minimum-hours threshold to ignore the noise of a few minutes.
* Risk level on the project: low, medium or high.
* One click to open the invoice wizard of the linked sales order.
* Ignore and reopen workflow with a chatter trail.
* Kanban, graph and pivot, multi-company isolation.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Project',
    'license': 'OPL-1',
    'price': 79.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'hr_timesheet',
        'sale',
        'account',
        'sale_timesheet',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/billable_gap_0_views.xml',
        'views/billable_scan_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
