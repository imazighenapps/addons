# -*- coding: utf-8 -*-
{
    'name': 'LeadTime',
    'version': '18.0.1.0.0',
    'summary': 'Compare promised supplier lead times with actual receipt dates and expose the drift that breaks your planning.',
    'description': '''LeadTime - Promises Measured In Days
====================================
Compare promised supplier lead times with actual receipt dates and expose the drift that breaks your planning.

Key points:
* Quoted lead times tracked in a dedicated register.
* Actual lead times recorded with clear ownership and dates.
* Supplier drift visible so nothing slips through.
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
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/leadtime_watch_entry_0_views.xml',
        'views/leadtime_watch_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
