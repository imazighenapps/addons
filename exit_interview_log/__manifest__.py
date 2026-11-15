# -*- coding: utf-8 -*-
{
    'name': 'ExitInterview',
    'version': '19.0.1.0.0',
    'summary': 'Record employee exit interviews with departure reasons, feedback and follow-up actions, track completion and review in a company-safe register.',
    'description': '''ExitInterview - Employee Exit Interview Log
===========================================
Exit interview feedback captured in unstructured notes is hard to review and
analyze. HR teams lose visibility on recurring departure reasons and actions.

ExitInterview provides a structured record per departing employee. Capture the
interview date, reasons, feedback and follow-up actions, then mark records as
completed and reviewed.

* Interview records with employee, date and departure reason.
* Feedback, highlights, concerns and follow-up actions.
* States: draft, completed, reviewed.
* Search and reporting by reason, department and period.
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
        'views/exit_interview_log_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
