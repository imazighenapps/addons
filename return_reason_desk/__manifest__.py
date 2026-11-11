# -*- coding: utf-8 -*-
{
    'name': 'ReturnInsight',
    'version': '19.0.1.0.0',
    'summary': 'Classify every sales return by reason and product to expose the quality or expectation issues that repeat.',
    'description': '''ReturnInsight - Returns Tell The Truth
======================================
Classify every sales return by reason and product to expose the quality or expectation issues that repeat.

Key points:
* Return reasons tracked in a dedicated register.
* Reason trends recorded with clear ownership and dates.
* Cost by reason visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
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
        'views/return_reason_entry_0_views.xml',
        'views/return_reason_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
