# -*- coding: utf-8 -*-
{
    'name': 'ReturnablePackageLog',
    'version': '19.0.1.0.0',
    'summary': 'Track pallets, crates and containers sent to partners and returned, with due dates and deposits.',
    'description': '''ReturnablePackageLog - Returnable Packaging Movement Register
=============================================================
Returnable packaging tracked in spreadsheets disappears and deposits are
never recovered.

ReturnablePackageLog provides a simple movement register.

* Movements with partner, packaging type and quantity.
* Outbound and inbound direction.
* Movement, due and return dates.
* Deposit amount at risk per movement.
* Draft, sent, returned, lost and cancelled states.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Inventory',
    'license': 'OPL-1',
    'price': 19.0,
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
        'views/returnable_package_log_0_views.xml',
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
