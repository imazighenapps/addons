# -*- coding: utf-8 -*-
{
    'name': 'VendorOnboard',
    'version': '20.0.1.0.0',
    'summary': 'Onboard new suppliers through a checklist of documents and validations before they can receive a purchase order.',
    'description': '''VendorOnboard - Approved Before First Order
===========================================
Onboard new suppliers through a checklist of documents and validations before they can receive a purchase order.

Key points:
* Onboarding steps tracked in a dedicated register.
* Required docs recorded with clear ownership and dates.
* Approved vendors visible so nothing slips through.
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
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/vendor_onboard_entry_0_views.xml',
        'views/vendor_onboard_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
