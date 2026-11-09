# -*- coding: utf-8 -*-
{
    'name': 'HireCheck',
    'version': '20.0.1.0.0',
    'summary': 'Launch a hire or an exit for an employee, get a starter checklist pushed into it, and close the file only when every task is done by its owner.',
    'description': '''HireCheck - Onboarding And Offboarding On Rails
===============================================
Every arrival is welcomed differently depending on who remembers what.
The Odoo account exists after three days, the desk is wrong, the safety
briefing is forgotten, and when somebody leaves the badge and the
equipment are recovered weeks later - or never. Nothing is written
down, so nothing can be improved either.

HireCheck opens one checklist per arrival or departure, directly on the
employee record. A new checklist is born with its starter tasks in it -
IT, admin and manager duties for a hire, equipment and access recovery
for an exit - and each task has an owner, a category and a due date.
The file starts, moves to done, and refuses to close while open tasks
remain; cancel and reopen leave a dated trace in the chatter. The same
standard applies to every colleague, from the first day to the last.

* One checklist per hire or exit, typed onboarding or offboarding.
* Starter tasks pushed automatically in every new file.
* Tasks owned by users with a category and a due date.
* Start, close, reopen and cancel states with a chatter trail.
* No closing while open tasks remain on the file.
* A company-wide task screen for every pending action.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Human Resources/Employee',
    'license': 'OPL-1',
    'price': 79.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/hire_check_0_views.xml',
        'views/hire_check_line_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
