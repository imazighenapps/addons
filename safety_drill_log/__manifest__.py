# -*- coding: utf-8 -*-
{
    'name': 'SafetyDrillLog',
    'version': '20.0.1.0.0',
    'summary': 'Record safety drills with type, date, participants, observations and corrective actions to keep an auditable drill history.',
    'description': '''SafetyDrillLog - Health and Safety Drill Register
=================================================
Safety drills are often documented informally, making it hard to prove
completion, track findings and close corrective actions.

SafetyDrillLog keeps a simple register of drills with observations and
follow-up.

* Drill records with type, date, location and responsible person.
* Participant count and attendance notes.
* Observations, findings and corrective actions.
* Draft, completed and cancelled states.
* Planned and performed dates.
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
        'hr',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/safety_drill_log_0_views.xml',
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
