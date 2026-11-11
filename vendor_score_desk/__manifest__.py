# -*- coding: utf-8 -*-
{
    'name': 'VendorScore',
    'version': '20.0.1.0.0',
    'summary': 'Score suppliers on delivery, quality and price over time and build a preferred-vendor list you can defend.',
    'description': '''VendorScore - Suppliers Scored, Not Guessed
===========================================
Score suppliers on delivery, quality and price over time and build a preferred-vendor list you can defend.

Key points:
* Scorecards tracked in a dedicated register.
* Quality & delay recorded with clear ownership and dates.
* Preferred vendors visible so nothing slips through.
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
        'views/vendor_score_entry_0_views.xml',
        'views/vendor_score_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
