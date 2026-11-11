# -*- coding: utf-8 -*-
{
    'name': 'TenderDesk',
    'version': '20.0.1.0.0',
    'summary': 'Run a simple tender: invite suppliers, compare bids side by side and record the award with a clear rationale.',
    'description': '''TenderDesk - Bids Compared, Awards Clear
========================================
Run a simple tender: invite suppliers, compare bids side by side and record the award with a clear rationale.

Key points:
* RFQ rounds tracked in a dedicated register.
* Supplier bids recorded with clear ownership and dates.
* Award decision visible so nothing slips through.
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
    'price': 89.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/tender_desk_entry_0_views.xml',
        'views/tender_desk_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
