# -*- coding: utf-8 -*-
{
    'name': 'GiftRegister',
    'version': '18.0.1.0.0',
    'summary': 'Record business gifts given or received with counterpart, value and purpose, track declaration and approval states, and keep a company-safe compliance register.',
    'description': '''GiftRegister - Business Gift and Hospitality Log
================================================
Gifts and hospitality declared by email or spreadsheets are hard to audit and may
breach policy when values are not tracked consistently.

GiftRegister provides a structured register for gifts given or received. Record
counterpart, value, purpose and responsible employee, then track declaration and
approval status for a clear audit trail.

* Gift records with direction, counterpart, date and value.
* Purpose and responsible employee.
* States: draft, declared, approved, refused.
* Search and reporting by direction, employee and period.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Services',
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
        'views/gift_register_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
