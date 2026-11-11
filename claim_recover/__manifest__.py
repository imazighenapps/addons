# -*- coding: utf-8 -*-
{
    'name': 'RecoverBook',
    'version': '20.0.1.0.0',
    'summary': 'Log every refund, rebate or reimbursement the company is owed by customers or suppliers and chase them.',
    'description': '''RecoverBook - Money Owed Back
=============================
A supplier promised a rebate, a carrier owes a refund, a customer must
reimburse a return fee: the amounts are real and the follow-up is
scattered across inboxes and sticky notes. Weeks pass, nobody knows what
is still outstanding, and the money the company is owed quietly expires
or is simply forgotten.

RecoverBook keeps one claim per amount owed back to you in Odoo. Each
claim records the counterparty, the origin document, the amount expected
and the date you first raised it, and you can log every chase action with
its date and a short note. The claim moves from open to recovered or
written off, the recovered amount is tracked against what was expected,
and the chase list shows only what is still due. The cash you are owed is
the cash the module keeps in sight.

* One claim per refund, rebate or reimbursement owed to the company.
* The counterparty, origin reference, amount and due date on each claim.
* Chase actions logged with a date and a note on every claim.
* A workflow to mark a claim as recovered or written off.
* The recovered amount tracked against the expected amount.
* One chase list for every claim still outstanding.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/recover_claim_0_views.xml',
        'views/recover_action_1_views.xml',
        'views/recover_chase_2_views.xml',
        'views/menus.xml',
        'views/recover_chase_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
