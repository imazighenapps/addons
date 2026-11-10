# -*- coding: utf-8 -*-
{
    'name': 'GuaranteeBook',
    'version': '18.0.1.0.0',
    'summary': 'Track every bank guarantee or standby letter from issue to release and never pay avoidable renewal fees.',
    'description': '''GuaranteeBook - Guarantees Released On Time
==========================================
Bank guarantees and standby letters live in a drawer: the issue date is in an
email, the expiry in a spreadsheet and the release in nobody's calendar. A
forgotten renewal becomes an automatic fee, and a guarantee that should have
been released keeps tying up credit long after the contract is over.

GuaranteeBook keeps one register per instrument with its type, beneficiary,
issuing bank, amount and validity period. The release can be recorded with the
exact date and a note, and every renewal is logged so the history of the
instrument stays readable. Active guarantees approaching expiry are easy to
spot, and the screen of released instruments shows what is no longer tying up
your credit line. The file you hand to the bank is the one the module already
holds.

* A register of bank guarantees and standby letters of credit.
* Beneficiary, issuing bank, amount and currency per instrument.
* Issue and expiry dates with a stored active-guarantee flag.
* Release recorded with the exact date and a closing note.
* A renewal history with the previous and new expiry dates.
* One screen for guarantees still active and due to watch.
* An early release refused when the date predates the issue.
* Multi-company isolation out of the box.''',
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
        'views/bank_guarantee_0_views.xml',
        'views/bank_guarantee_renewal_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
