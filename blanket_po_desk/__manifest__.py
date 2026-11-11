# -*- coding: utf-8 -*-
{
    'name': 'BlanketPO',
    'version': '20.0.1.0.0',
    'summary': 'Manage blanket purchase agreements with call-off orders and track the committed value still available.',
    'description': '''BlanketPO - Commit Once, Call Off Often
=======================================
Manage blanket purchase agreements with call-off orders and track the committed value still available.

Key points:
* Framework POs tracked in a dedicated register.
* Call-off orders recorded with clear ownership and dates.
* Remaining value visible so nothing slips through.
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
        'views/blanket_po_entry_0_views.xml',
        'views/blanket_po_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
