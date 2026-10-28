# -*- coding: utf-8 -*-
{
    'name': 'ProjectMargin - Project Profitability and Budget Control',
    'version': '20.0.1.0.0',
    'summary': 'Track budgeted and actual revenue and cost per project, watch the margin rate and get flagged before a cost overrun eats the profit.',
    'description': '''ProjectMargin - Project Profitability and Budget Control
========================================================
A project is sold with a comfortable margin. Three change requests, two
extra subcontractors and one forgotten licence later, the margin has
silently disappeared - and nobody notices before the closing meeting.

ProjectMargin puts the budget and the actuals side by side on a single
screen. Enter the budget revenue and the budget cost when the project is
quoted, then record every revenue and cost line as it happens: labor,
material, subcontract, expense or other, with the invoice reference when
there is one. Actual revenue, actual cost, actual margin and margin rate
are recomputed on the fly, and the cost ratio shows how much of the cost
budget has already been consumed. When the actual cost passes the budget
cost by more than the alert threshold, the project is flagged as over
budget before it is too late. Closing the project freezes its budget and
its lines, and the whole story stays in the chatter.

* Budget revenue and budget cost per project.
* Revenue and cost lines with category and invoice reference.
* Actual revenue, cost, margin and margin rate, always up to date.
* Cost ratio against the budget cost.
* Overrun alert above a configurable threshold.
* Draft, running and closed states with an audit trail.
* Budget and lines locked once the project is closed.
* Multi-company, multi-currency, no Enterprise dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Services/Project',
    'license': 'OPL-1',
    'price': 79.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'project',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/margin_project_0_views.xml',
        'views/margin_line_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
