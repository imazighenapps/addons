# -*- coding: utf-8 -*-
{
    'name': 'KeyCustody',
    'version': '18.0.1.0.0',
    'summary': 'Register physical keys and badges, track issuance and return per employee, mark items issued, returned or lost, and keep a company-safe custody history.',
    'description': '''KeyCustody - Key and Badge Issuance Tracking
============================================
Physical keys and access badges are easy to lose track of when sign-outs live on
paper. Security and facilities teams need to know who holds each item and when it
was returned.

KeyCustody provides a catalogue of keys/badges and a custody log. Issue an item to
an employee, record its return or mark it lost so the current holder and history
are always visible.

* Key/badge items with identifier, type and active flag.
* Custody records linking item to employee with issue/return dates.
* States: issued, returned, lost.
* Search and reporting by item, employee and state.
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
        'views/key_custody_0_views.xml',
        'views/key_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
