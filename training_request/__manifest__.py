# -*- coding: utf-8 -*-
{
    'name': 'TrainingRequest',
    'version': '19.0.1.0.0',
    'summary': 'Submit and approve employee training requests with topic, provider and estimated cost, track status through review and completion in a company-safe register.',
    'description': '''TrainingRequest - Employee Training Request and Approval
=======================================================
Training needs requested by email or chat are easy to lose and hard to prioritize.
Managers lack a consolidated view for approval and HR cannot track planned training.

TrainingRequest provides a structured request workflow. Employees submit the
training topic, dates and estimated cost; managers approve or refuse and HR can
track requests through completion.

* Requests with employee, topic, provider and estimated cost.
* Requested dates and justification.
* States: draft, submitted, approved, refused, done.
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
        'views/training_request_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
