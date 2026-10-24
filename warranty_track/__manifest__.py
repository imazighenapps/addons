# -*- coding: utf-8 -*-
{
    'name': 'WarrantyTrack - Product Warranty and Claims',
    'version': '19.0.1.0.0',
    'summary': 'Register the warranty of every serial number, check coverage at claim time, record repair or replacement cost and recover from the supplier.',
    'description': '''WarrantyTrack - Product Warranty and Claims
============================================
Know instantly whether a product is still under warranty.

WarrantyTrack registers a warranty per customer, product and serial number,
with a start date and a duration. When the customer comes back, the claim
screen shows in one second whether the product is covered. You record the
repair or replacement, its real cost, and how much you recovered from the
supplier.

* Warranty per customer, product, serial number and invoice.
* Automatic end date and coverage status.
* Claim workflow: draft, approved, repaired, refused.
* Coverage check at claim creation.
* Repair or replacement cost and supplier recovery.
* Claims linked to the warranty and the customer.
* Expiry scheduler for the warranty list.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Services/Field Service',
    'license': 'OPL-1',
    'price': 79.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'sale',
        'stock',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/warranty_registration_0_views.xml',
        'views/warranty_claim_1_views.xml',
        'views/menus.xml',
        'data/cron.xml',
        'views/sale_order_inherit.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
