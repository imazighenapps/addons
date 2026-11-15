# -*- coding: utf-8 -*-
{
    'name': 'PestControlLog',
    'version': '18.0.1.0.0',
    'summary': 'Record pest control visits with provider, area, findings, treatment notes and states to keep a traceable intervention history.',
    'description': '''PestControlLog - Pest Control Intervention Register
===================================================
Pest control interventions are often documented in provider reports and
emails, making treatment history hard to retrieve for audits.

PestControlLog keeps a simple register of visits, findings and follow-up.

* Intervention records with date, provider, area and responsible person.
* Pest type, findings and treatment notes.
* Scheduled and completed dates with follow-up notes.
* Draft, scheduled, done and cancelled states.
* Visit history per area.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Project',
    'license': 'OPL-1',
    'price': 29.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'contacts',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/pest_control_log_0_views.xml',
        'views/menus.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
