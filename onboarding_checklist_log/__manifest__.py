# -*- coding: utf-8 -*-
{
    'name': 'OnboardLog',
    'version': '20.0.1.0.0',
    'summary': 'Track new employee onboarding with checklist tasks, owners and due dates, monitor progress through states, and keep a company-safe completion record.',
    'description': '''OnboardLog - Employee Onboarding Checklist Log
==============================================
Onboarding tasks managed in ad-hoc lists are easy to miss, delaying new hire
productivity and creating inconsistent experiences.

OnboardLog provides a structured onboarding record per employee with checklist
task lines. Assign owners and due dates, track completion, and mark onboarding as
done when key tasks are completed.

* Onboarding records per employee with start date and responsible.
* Checklist task lines with owner, due date and done status.
* States: draft, in progress, done, cancelled.
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
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/onboarding_checklist_0_views.xml',
        'views/onboarding_checklist_line_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
