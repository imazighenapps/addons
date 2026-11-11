# -*- coding: utf-8 -*-
{
    'name': 'VisitorDesk',
    'version': '19.0.1.0.0',
    'summary': 'Register site visitors, issue temporary badges and always know who is on site at any moment.',
    'description': '''VisitorDesk - Every Visitor Accounted For
=========================================
Register site visitors, issue temporary badges and always know who is on site at any moment.

Key points:
* Visitor log tracked in a dedicated register.
* Badges issued recorded with clear ownership and dates.
* On-site now visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
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
        'views/visitor_desk_entry_0_views.xml',
        'views/visitor_desk_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
