# -*- coding: utf-8 -*-
{
    'name': 'BarcodeDesk',
    'version': '19.0.1.0.0',
    'summary': 'Attach multiple barcodes per product and packaging so every scan in the warehouse resolves correctly.',
    'description': '''BarcodeDesk - Every Scan Resolves
=================================
Attach multiple barcodes per product and packaging so every scan in the warehouse resolves correctly.

Key points:
* Extra barcodes tracked in a dedicated register.
* Pack barcodes recorded with clear ownership and dates.
* Scan log visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Inventory',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/multi_barcode_entry_0_views.xml',
        'views/multi_barcode_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
