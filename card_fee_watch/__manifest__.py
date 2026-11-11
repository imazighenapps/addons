# -*- coding: utf-8 -*-
{
    'name': 'FeeWatch',
    'version': '19.0.1.0.0',
    'summary': 'Compare what your payment platform charges with the rate you signed and recover every unexpected fee.',
    'description': '''FeeWatch - Fees Signed, Fees Charged
====================================
Payment platforms publish tidy rate cards and then bill whatever their
month-end file says. A percentage point here, a fixed fee there, and the
finance team only notices the drift once the money is already gone.
Disputing it later means hunting the signed contract, rebuilding the
expected amount on a spreadsheet and hoping the platform agrees.

FeeWatch keeps the expected fee schedule you signed in Odoo: one
contract per provider with its percentage rate and its fixed amount per
transaction. Every billed fee you receive is recorded against that
contract with the settled amount and the fee actually charged, and the
expected fee and variance are computed and stored for you. A review
step lets you mark a line as disputed or recovered so nothing is
forgotten, and the variance screen shows exactly which charges deserve
a claim. The figure you contest is the figure the module already
explains.

* Fee contracts with provider, percentage rate and fixed amount.
* Billed fee lines with settled amount and fee actually charged.
* Expected fee and variance computed and stored on every line.
* A workflow to dispute, recover or waive an unexpected fee.
* One variance screen for every line that differs from the contract.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 45.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/fee_contract_0_views.xml',
        'views/fee_line_1_views.xml',
        'views/fee_variance_2_views.xml',
        'views/menus.xml',
        'views/fee_variance_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
