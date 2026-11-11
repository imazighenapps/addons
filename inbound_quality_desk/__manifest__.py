# -*- coding: utf-8 -*-
{
    'name': 'InboundQA',
    'version': '19.0.1.0.0',
    'summary': 'Run inbound quality checks on receipts and block nonconforming lots before they enter available stock.',
    'description': '''InboundQA - Bad Stock Stays Out
===============================
Run inbound quality checks on receipts and block nonconforming lots before they enter available stock.

Key points:
* Receipt checks tracked in a dedicated register.
* Inspection results recorded with clear ownership and dates.
* Blocked lots visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Warehouse and Storage',
    'license': 'OPL-1',
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/inbound_quality_entry_0_views.xml',
        'views/inbound_quality_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
