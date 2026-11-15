# -*- coding: utf-8 -*-
{
    'name': 'WarrantyClaimLog',
    'version': '20.0.1.0.0',
    'summary': 'Register warranty claims with customer, product, issue details and resolution states to track after-sales follow-up.',
    'description': '''WarrantyClaimLog - Warranty Claim Register
==========================================
Warranty requests handled by email or spreadsheets are easy to lose track of,
delaying responses and making outcomes hard to audit.

WarrantyClaimLog provides a simple register for each claim with its status
and resolution.

* Claim records with customer, product and sale reference.
* Issue description, serial/lot reference and dates.
* Responsible user and planned resolution date.
* Draft, in review, approved, resolved and rejected states.
* Resolution notes and outcome.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'contacts',
        'sale',
        'product',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/warranty_claim_log_0_views.xml',
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
