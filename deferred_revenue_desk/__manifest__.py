# -*- coding: utf-8 -*-
{
    'name': 'DeferRevenue',
    'version': '20.0.1.0.0',
    'summary': 'Spread prepaid revenue over the service period and post the recognition entries automatically each month.',
    'description': '''DeferRevenue - Revenue Earned, Not Rushed
=========================================
Spread prepaid revenue over the service period and post the recognition entries automatically each month.

Key points:
* Deferral schedules tracked in a dedicated register.
* Monthly recognition recorded with clear ownership and dates.
* Remaining balance visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/deferred_revenue_entry_0_views.xml',
        'views/deferred_revenue_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
