# -*- coding: utf-8 -*-
{
    'name': 'SupplierBreak',
    'version': '18.0.1.0.0',
    'summary': 'Store supplier quantity price breaks and highlight the order quantity that lands the best unit cost.',
    'description': '''SupplierBreak - Order The Smart Quantity
========================================
Store supplier quantity price breaks and highlight the order quantity that lands the best unit cost.

Key points:
* Supplier tiers tracked in a dedicated register.
* Break prices recorded with clear ownership and dates.
* Best quantity visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Purchase/Purchase',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/price_break_entry_0_views.xml',
        'views/price_break_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
