# -*- coding: utf-8 -*-
{
    'name': 'CallSheet',
    'version': '20.0.1.0.0',
    'summary': 'Plan outbound call lists with priorities and log outcomes so no promised callback is forgotten.',
    'description': '''CallSheet - Every Call, Every Callback
======================================
Plan outbound call lists with priorities and log outcomes so no promised callback is forgotten.

Key points:
* Call plans tracked in a dedicated register.
* Call outcomes recorded with clear ownership and dates.
* Follow-up queue visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'CRM/CRM',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/call_sheet_entry_0_views.xml',
        'views/call_sheet_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
