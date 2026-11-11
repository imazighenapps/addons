# -*- coding: utf-8 -*-
{
    'name': 'PayPlan',
    'version': '18.0.1.0.0',
    'summary': 'Split an invoice into an agreed installment plan and track each due date and payment against the schedule.',
    'description': '''PayPlan - Pay In Agreed Steps
=============================
Split an invoice into an agreed installment plan and track each due date and payment against the schedule.

Key points:
* Installment plans tracked in a dedicated register.
* Due schedule recorded with clear ownership and dates.
* Plan balance visible so nothing slips through.
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
        'views/payment_plan_entry_0_views.xml',
        'views/payment_plan_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
