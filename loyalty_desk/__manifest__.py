# -*- coding: utf-8 -*-
{
    'name': 'PointsBank',
    'version': '18.0.1.0.0',
    'summary': 'Reward every paid invoice with points your customers can redeem on the next order, with a clean point ledger.',
    'description': '''PointsBank - Points Your Customers Bank
=======================================
Loyalty rewards are often tracked in a side spreadsheet: points are granted
after a payment, redeemed on the next order, and the balance is whatever
someone last calculated by hand. Customers question their balance, staff
cannot prove how points were earned or spent, and expired promises live on
forever.

PointsBank gives each customer a point account in Odoo with a dated ledger
of every movement. Each entry earns or redeems points against the same
account, and the running balance is computed and stored from the ledger.
Accounts can be suspended when needed, redemptions that would push the
balance below zero are refused, and every movement is traced with a
reference. The balance your customer asks for is the one the ledger already
shows.

* A point account per customer with a live stored balance.
* Earn and redeem movements recorded in a dated ledger.
* A running balance computed from every ledger entry.
* References kept on each movement for traceability.
* Accounts that can be suspended when needed.
* Redemptions that would overdraw the balance are refused for you.
* Negative earn amounts are refused for you.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'price': 79.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/loyalty_account_0_views.xml',
        'views/loyalty_move_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
