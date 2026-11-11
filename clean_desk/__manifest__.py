# -*- coding: utf-8 -*-
{
    'name': 'HygieneBook',
    'version': '20.0.1.0.0',
    'summary': 'Schedule who cleans what, when and how, keep the dated proof and show the areas still waiting.',
    'description': '''HygieneBook - Cleaned, Dated, Proven
====================================
Cleaning routines are planned on whiteboards and signed on paper
sheets that disappear when the audit arrives. Nobody can quickly tell
which area is still waiting, who was responsible for the last pass or
whether the method requested was actually followed.

HygieneBook turns each cleaning routine into a plan with the area,
the frequency, the method and the responsible team. Every execution
is logged with its scheduled date, performer and completion time so
the proof is dated and attributable. Pending executions stay visible
until they are completed, and plans show how much work is still open
at a glance.

* Cleaning plans with area, frequency, method and owner.
* Execution logs with schedule, performer and completion date.
* A workflow from planned to done or cancelled.
* Pending executions filtered for areas still waiting.
* Completion refused when the execution date is missing.
* Stored counters for executions and pending work.
* Notes kept on each plan and execution for the audit file.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
    'license': 'OPL-1',
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/cln_plan_0_views.xml',
        'views/cln_execution_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
