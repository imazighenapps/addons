# -*- coding: utf-8 -*-
{
    'name': 'ReferBook',
    'version': '18.0.1.0.0',
    'summary': 'Give every customer a referral code, credit the reward when the referred friend orders and rank your advocates.',
    'description': '''ReferBook - Referrals That Pay
==============================
Referral programs are often run informally: a customer shares a name, the
team promises a reward, and nobody can say which code brought which order or
whether the reward was actually credited. Advocates feel forgotten and the
cost of the program is impossible to measure.

ReferBook gives every advocate a referral code in Odoo and records each
referred friend on that code. When the referred order is confirmed, the
reward can be credited with one action and the code totals are updated from
its referrals. Referrals move from pending to credited or cancelled, codes
can be closed when a campaign ends, and a credited referral cannot be
credited twice. The ranking of your advocates is the one the register
already computes.

* A unique referral code per advocate with active and closed states.
* Referred friends recorded with order amount and reward value.
* One-click crediting that stamps the reward date.
* Referral totals and rewards computed and stored on each code.
* A referral workflow from pending to credited or cancelled.
* Crediting a cancelled or already credited referral is refused for you.
* Closing a code without touching its history is supported.
* Multi-company isolation out of the box.''',
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
        'views/refer_code_0_views.xml',
        'views/refer_referral_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
