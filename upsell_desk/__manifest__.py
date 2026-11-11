# -*- coding: utf-8 -*-
{
    'name': 'UpsellDesk',
    'version': '18.0.1.0.0',
    'summary': 'Suggest the right accessory or upgrade on each quote from simple rules and measure the add-ons your team actually sells.',
    'description': '''UpsellDesk - The Add-On They Needed
===================================
Suggest the right accessory or upgrade on each quote from simple rules and measure the add-ons your team actually sells.

Key points:
* Upsell rules tracked in a dedicated register.
* Suggested adds recorded with clear ownership and dates.
* Won add-ons visible so nothing slips through.
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
        'views/upsell_desk_entry_0_views.xml',
        'views/upsell_desk_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
