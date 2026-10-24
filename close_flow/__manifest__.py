# -*- coding: utf-8 -*-
{
    'name': 'CloseFlow - Month-End Close Checklist',
    'version': '20.0.1.0.0',
    'summary': 'Run the monthly close with a reusable checklist: owners, deadlines, dependencies, evidence, progress dashboard and a locked audit trail.',
    'description': '''CloseFlow - Month-End Close Checklist
=====================================
Close the month on time, with proof, every month.

CloseFlow turns your closing checklist into a controlled workflow. Build a
template once, generate the period in one click, and every task gets an owner
and a deadline. A task cannot be completed while its predecessor is open or
while the required evidence is missing. When everything is done the period is
locked: no task can be changed anymore, and the history stays as an audit
trail.

* Reusable close template with tasks, owners and deadlines.
* Period generation in one click.
* Task dependencies: no shortcut, no forgotten step.
* Mandatory evidence (attachment) per task.
* Progress bar and dashboard per period.
* Lock the period when the close is finished.
* Only a manager can unlock a closed period.
* Full audit trail: who completed what, when, with which proof.
* Multi-company.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 79.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/close_period_0_views.xml',
        'views/close_task_1_views.xml',
        'views/close_template_2_views.xml',
        'views/close_template_line_3_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
