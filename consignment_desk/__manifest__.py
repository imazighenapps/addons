# -*- coding: utf-8 -*-
{
    'name': 'ConsignDesk',
    'version': '20.0.1.0.0',
    'summary': 'Track vendor-owned consignment stock on your site and settle only what you actually consumed.',
    'description': '''ConsignDesk - Pay For What You Used
===================================
Track vendor-owned consignment stock on your site and settle only what you actually consumed.

Key points:
* Consignment stock tracked in a dedicated register.
* Usage draws recorded with clear ownership and dates.
* Vendor settlements visible so nothing slips through.
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
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/consignment_desk_entry_0_views.xml',
        'views/consignment_desk_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
