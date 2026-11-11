# -*- coding: utf-8 -*-
{
    'name': 'RoundOff',
    'version': '19.0.1.0.0',
    'summary': 'Absorb the one-cent and rounding differences between invoices, payments and statements with clean write-offs.',
    'description': '''RoundOff - One Cent, Cleanly Gone
=================================
A payment lands one cent short, a bank statement rounds the other way,
and the open balance sits there for months because nobody wants to book a
manual adjustment. These tiny differences are harmless alone and messy in
bulk: they clutter the aged balance, block reconciliations and turn a
clean close into a hunt for pennies.

RoundOff keeps simple write-off rules in Odoo with a maximum amount you
accept to absorb and the reason you will book. Every small difference is
recorded as a write-off against a rule with its source reference and the
amount to clear, and a single action posts it so the queue empties in one
place. Differences above the rule limit are refused, and the cleared
screen shows what was absorbed and when. The cent that blocked the close
is the cent the module cleared on purpose.

* Write-off rules with a maximum amount and a clear reason.
* Small-difference write-offs linked to a rule and a source reference.
* A posted state that records the date the amount was cleared.
* Amounts above the rule limit refused for you.
* One cleared queue for every absorbed difference.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 29.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/round_rule_0_views.xml',
        'views/round_writeoff_1_views.xml',
        'views/round_cleared_2_views.xml',
        'views/menus.xml',
        'views/round_cleared_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
