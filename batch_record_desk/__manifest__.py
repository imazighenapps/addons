# -*- coding: utf-8 -*-
{
    'name': 'BatchRecord',
    'version': '19.0.1.0.0',
    'summary': 'Build electronic batch records with step-by-step sign-offs so each batch is released on documented evidence.',
    'description': '''BatchRecord - Batches Released On Proof
=======================================
Build electronic batch records with step-by-step sign-offs so each batch is released on documented evidence.

Key points:
* Batch records tracked in a dedicated register.
* Step sign-offs recorded with clear ownership and dates.
* Release decision visible so nothing slips through.
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
    'price': 79.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/batch_record_entry_0_views.xml',
        'views/batch_record_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
