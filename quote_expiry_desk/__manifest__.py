# -*- coding: utf-8 -*-
{
    'name': 'QuoteExpiry',
    'version': '18.0.1.0.0',
    'summary': 'Monitor quotation validity dates and prompt sales to renew or close offers before they silently expire.',
    'description': '''QuoteExpiry - No Offer Left To Expire
=====================================
Monitor quotation validity dates and prompt sales to renew or close offers before they silently expire.

Key points:
* Expiring quotes tracked in a dedicated register.
* Validity dates recorded with clear ownership and dates.
* Renewal queue visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
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
        'views/quote_expiry_entry_0_views.xml',
        'views/quote_expiry_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
