# -*- coding: utf-8 -*-
{
    'name': 'DamageClaim',
    'version': '18.0.1.0.0',
    'summary': 'Record damaged receipts and shipments, file the carrier claim and track the compensation until it lands.',
    'description': '''DamageClaim - Damage Claimed, Value Back
========================================
Record damaged receipts and shipments, file the carrier claim and track the compensation until it lands.

Key points:
* Damage reports tracked in a dedicated register.
* Carrier claims recorded with clear ownership and dates.
* Recovered value visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Inventory',
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
        'views/damage_claim_entry_0_views.xml',
        'views/damage_claim_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
