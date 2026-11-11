# -*- coding: utf-8 -*-
{
    'name': 'TargetBook',
    'version': '20.0.1.0.0',
    'summary': 'Set periodic sales targets per rep or team and track actual performance and gaps in real time.',
    'description': '''TargetBook - Targets Visible, Gaps Known
========================================
Set periodic sales targets per rep or team and track actual performance and gaps in real time.

Key points:
* Sales targets tracked in a dedicated register.
* Actual vs target recorded with clear ownership and dates.
* Gap by rep visible so nothing slips through.
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
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/sales_target_entry_0_views.xml',
        'views/sales_target_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
