# -*- coding: utf-8 -*-
{
    'name': 'ContractExpiry',
    'version': '18.0.1.0.0',
    'summary': 'Register agreements with partners, track end and notice dates, surface upcoming expiries and follow renewal or closure states.',
    'description': '''ContractExpiry - Contract and Expiry Tracker
============================================
Missed renewals and unnoticed expiries create service gaps or unwanted
auto-renewals. Key dates are often buried in spreadsheets and documents.

ContractExpiry keeps a simple register of agreements with their partner,
reference, dates and responsible owner, and highlights what expires soon.

* Contract records with partner, reference, start, end and notice date.
* Responsible user, type and notes.
* Draft, active, expiring, renewed and closed states.
* Days to expiry computed from the end date.
* Filters for upcoming expiries and states.
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
        'views/contract_expiry_log_0_views.xml',
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
