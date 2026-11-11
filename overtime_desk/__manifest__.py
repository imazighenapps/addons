# -*- coding: utf-8 -*-
{
    'name': 'OverTime',
    'version': '19.0.1.0.0',
    'summary': 'Collect overtime requests per employee, approve them properly and keep the hours each team banked.',
    'description': '''OverTime - Extra Hours, Properly Owned
======================================
Extra hours often start as a quick message and end as a dispute at
payroll time. Requests arrive without context, approvals are implicit,
and nobody can say with confidence how many hours each employee or team
has already accumulated this period. Managers spend their evenings
rebuilding the story from calendars and chat logs.

OverTime centralizes overtime requests in Odoo so every extra hour is
declared, reviewed and approved in the same place. Each request records
the employee, the date, the number of hours and the reason for the
overtime, then follows a clear workflow from draft to approval or
rejection. Employees and managers can group requests by person,
department or period to understand the banked hours before they become
a payroll surprise.

The module keeps a lightweight but auditable trail of who asked, who
approved and how much time was actually granted, making extra hours a
managed decision rather than an informal habit.

* Overtime requests per employee with date, hours and reason.
* A clear workflow from draft to approved or rejected.
* Stored counters of requested and approved hours per request line.
* Grouping by employee and state for quick team reviews.
* Chatter tracking on every request for decisions and comments.
* Validation to refuse negative or zero-hour requests.
* Refusal of approval without a responsible review step.
* Multi-company isolation with autonomous employee records in tests.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Human Resources/Employee',
    'license': 'OPL-1',
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/overtime_request_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
