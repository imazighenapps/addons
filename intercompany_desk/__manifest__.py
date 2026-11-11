# -*- coding: utf-8 -*-
{
    'name': 'IntercoBook',
    'version': '20.0.1.0.0',
    'summary': 'Mirror intercompany invoices and bills between sister companies and reconcile the balances they must share.',
    'description': '''IntercoBook - Sister Books In Balance
=====================================
Mirror intercompany invoices and bills between sister companies and reconcile the balances they must share.

Key points:
* Intercompany pairs tracked in a dedicated register.
* Mirror entries recorded with clear ownership and dates.
* Balance check visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 79.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/intercompany_desk_entry_0_views.xml',
        'views/intercompany_desk_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
