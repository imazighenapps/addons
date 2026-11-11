# -*- coding: utf-8 -*-
{
    'name': 'DepositDesk',
    'version': '19.0.1.0.0',
    'summary': 'Take deposits on booked appointments and track no-shows so valuable slots are protected.',
    'description': '''DepositDesk - Slots Worth Showing Up For
========================================
Take deposits on booked appointments and track no-shows so valuable slots are protected.

Key points:
* Booked slots tracked in a dedicated register.
* Deposits taken recorded with clear ownership and dates.
* No-show log visible so nothing slips through.
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
        'views/appointment_deposit_entry_0_views.xml',
        'views/appointment_deposit_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
