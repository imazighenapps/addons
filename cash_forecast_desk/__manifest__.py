# -*- coding: utf-8 -*-
{
    'name': 'CashCast',
    'version': '19.0.1.0.0',
    'summary': 'Forecast the cash position from due receivables, payables and planned moves week by week.',
    'description': '''CashCast - Cash Seen Weeks Ahead
================================
Forecast the cash position from due receivables, payables and planned moves week by week.

Key points:
* Expected inflows tracked in a dedicated register.
* Expected outflows recorded with clear ownership and dates.
* Cash position visible so nothing slips through.
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
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/cash_forecast_entry_0_views.xml',
        'views/cash_forecast_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
