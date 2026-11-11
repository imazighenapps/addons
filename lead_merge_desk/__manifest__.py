# -*- coding: utf-8 -*-
{
    'name': 'LeadMerge',
    'version': '19.0.1.0.0',
    'summary': 'Detect likely duplicate leads and contacts and merge them safely so the pipeline counts every prospect once.',
    'description': '''LeadMerge - One Prospect, One Record
====================================
Detect likely duplicate leads and contacts and merge them safely so the pipeline counts every prospect once.

Key points:
* Duplicate leads tracked in a dedicated register.
* Merge review recorded with clear ownership and dates.
* Clean pipeline visible so nothing slips through.
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
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/lead_merge_entry_0_views.xml',
        'views/lead_merge_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
