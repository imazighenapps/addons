# -*- coding: utf-8 -*-
{
    'name': 'GiftWallet - Gift Cards and Store Credit',
    'version': '19.0.1.0.0',
    'summary': 'Issue gift cards with a unique code, redeem partially, reload, track the balance and expire them automatically.',
    'description': '''GiftWallet - Gift Cards and Store Credit
========================================
Sell gift cards and store credit in Odoo Community, without Enterprise.

GiftWallet issues a card with a unique code and a balance. Each redemption
creates a transaction and decreases the balance until the card is empty.
You can reload a card, extend its expiry date, and follow the outstanding
liability at any time.

* Unique card code, ready to print with a QR code.
* Issue, redeem partially, reload and cancel.
* Balance and full transaction history.
* Automatic expiry with a daily scheduler.
* Outstanding liability report for accounting.
* Works with POS, e-commerce and back-office sales.
* Multi-company and multi-currency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'sale',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/gift_card_0_views.xml',
        'views/gift_redeem_wizard_1_views.xml',
        'views/menus.xml',
        'data/cron.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
