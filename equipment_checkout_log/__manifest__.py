# -*- coding: utf-8 -*-
{
    'name': 'EquipmentCheckoutLog',
    'version': '18.0.1.0.0',
    'summary': 'Record shared equipment checkouts and returns with borrower, dates, condition notes and tracked states.',
    'description': '''EquipmentCheckoutLog - Equipment Checkout Register
==================================================
Shared equipment checked out informally leads to missing items and unclear
availability.

EquipmentCheckoutLog provides a simple checkout and return register.

* Checkout records with equipment, borrower and dates.
* Expected and actual return dates.
* Responsible issuer and condition notes.
* Draft, checked out, returned and cancelled states.
* Checkout history per item.
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
        'maintenance',
        'hr',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/equipment_checkout_log_0_views.xml',
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
