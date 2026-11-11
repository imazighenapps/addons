# -*- coding: utf-8 -*-
{
    'name': 'RentalDesk',
    'version': '18.0.1.0.0',
    'summary': 'Manage rentable products with pickup, return dates and charges so nothing stays out longer than paid for.',
    'description': '''RentalDesk - Out, Back, And Billed
==================================
Manage rentable products with pickup, return dates and charges so nothing stays out longer than paid for.

Key points:
* Rental orders tracked in a dedicated register.
* Out and back recorded with clear ownership and dates.
* Rental charges visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Services',
    'license': 'OPL-1',
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/rental_desk_entry_0_views.xml',
        'views/rental_desk_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
