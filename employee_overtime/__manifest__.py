# -*- coding: utf-8 -*-
{
    'name': 'OvertimeLog',
    'version': '19.0.1.0.0',
    'summary': 'Record employee overtime requests with date, hours and reason, run a submit/approve/refuse workflow, and report overtime by employee and period in a company-safe register.',
    'description': '''OvertimeLog - Employee Overtime Requests and Approval
====================================================
Overtime communicated by email or chat is hard to approve, track and reconcile.
Disputes arise when there is no consistent record of requested and approved hours.

OvertimeLog provides a structured overtime register. Employees or managers record
overtime with date, hours and reason, submit it for review and capture approval or
refusal so HR keeps a traceable history per employee and period.

* Overtime requests with employee, date, hours and reason.
* Submit, approve and refuse workflow states.
* Optional type/category and notes.
* Search and reporting by employee, state and period.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Human Resources/Employee',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'hr',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/employee_overtime_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
