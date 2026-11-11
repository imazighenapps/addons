# -*- coding: utf-8 -*-
{
    'name': 'KitDesk',
    'version': '18.0.1.0.0',
    'summary': 'Define sellable kits, assemble them on demand and consume components with a clear trace of every kit built.',
    'description': '''KitDesk - Kits Built On Demand
==============================
Define sellable kits, assemble them on demand and consume components with a clear trace of every kit built.

Key points:
* Kit definitions tracked in a dedicated register.
* Kit assembly recorded with clear ownership and dates.
* Component use visible so nothing slips through.
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
        'views/kitting_desk_entry_0_views.xml',
        'views/kitting_desk_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
