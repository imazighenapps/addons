# -*- coding: utf-8 -*-
{
    'name': 'QuoteKit',
    'version': '18.0.1.0.0',
    'summary': 'Assemble quotations from reusable section templates so complex offers go out fast and consistent every time.',
    'description': '''QuoteKit - Quotes Built In Minutes
==================================
Assemble quotations from reusable section templates so complex offers go out fast and consistent every time.

Key points:
* Reusable sections tracked in a dedicated register.
* Template lines recorded with clear ownership and dates.
* Fast quotes visible so nothing slips through.
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
        'views/quote_template_entry_0_views.xml',
        'views/quote_template_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
