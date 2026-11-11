# -*- coding: utf-8 -*-
{
    'name': 'PettyExpense',
    'version': '18.0.1.0.0',
    'summary': 'Log small out-of-pocket expenses with receipts against a petty cash balance and reconcile it in minutes.',
    'description': '''PettyExpense - Small Spends, Fully Traced
=========================================
Log small out-of-pocket expenses with receipts against a petty cash balance and reconcile it in minutes.

Key points:
* Small expenses tracked in a dedicated register.
* Receipt capture recorded with clear ownership and dates.
* Expense balance visible so nothing slips through.
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
        'views/petty_expense_entry_0_views.xml',
        'views/petty_expense_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
