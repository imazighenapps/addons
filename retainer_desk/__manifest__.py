# -*- coding: utf-8 -*-
{
    'name': 'RetainerBook',
    'version': '19.0.1.0.0',
    'summary': 'Sell hours in advance as retainers and show each customer how their bank burns down contract after contract.',
    'description': '''RetainerBook - Hours Visible, Always
====================================
Retainers are sold as a bank of hours, but the burn-down is often kept
in a private spreadsheet that only the account manager can read. Clients
ask how many hours remain, the answer takes a day, and the team keeps
working after the bank is empty because nobody saw the threshold.

RetainerBook records each retainer bank per customer with the hours
purchased, a validity window and a low-balance alert threshold. Every
usage entry logs the date and hours consumed, and the remaining hours
and burn-down percentage are computed and stored on the bank so the
status is always visible. Closing a bank freezes it while keeping the
history, and the usage is refused when it would consume more hours than
remain. Multi-company isolation keeps each company in its own book.

* A retainer bank per customer with purchased hours and validity dates.
* Usage entries that log the hours consumed over time.
* Remaining hours and burn-down percentage computed and stored.
* A low-balance threshold to flag banks running out of hours.
* Close and reopen actions to freeze or reactivate a bank.
* Usage above the remaining balance is refused for you.
* Customer-linked banks with a clear burn-down history.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Services',
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
        'views/retainer_bank_0_views.xml',
        'views/retainer_usage_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
