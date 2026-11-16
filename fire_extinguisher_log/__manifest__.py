# -*- coding: utf-8 -*-
{
    'name': 'FireExtinguisherLog',
    'version': '19.0.1.0.0',
    'summary': 'Record fire extinguisher inspections with location, type, dates, pressure and seal results.',
    'description': '''FireExtinguisherLog - Fire Extinguisher Inspection Register
===========================================================
Extinguisher checks kept on paper tags make due dates and failures hard to
prove.

FireExtinguisherLog provides a simple inspection register.

* Extinguisher records with reference, type, capacity and location.
* Last and next inspection dates.
* Pressure and seal check results.
* Responsible inspector and notes.
* Draft, validated, overdue and cancelled states.
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
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/fire_extinguisher_log_0_views.xml',
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
