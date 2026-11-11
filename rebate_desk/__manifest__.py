# -*- coding: utf-8 -*-
{
    'name': 'RebateBook',
    'version': '18.0.1.0.0',
    'summary': 'Accrue the annual volume rebate you promised per customer, watch it grow with each invoice and settle it once a year.',
    'description': '''RebateBook - Rebates Accrued On Time
====================================
Volume rebates are promised in a contract, tracked in a spreadsheet and
settled when someone remembers to look. Each new invoice should move the
accrual forward, but the amount owed to the customer drifts between
sales, accounting and the year-end meeting. When settlement day comes,
there is no single figure everyone can trust.

RebateBook keeps one contract per customer and rebate period with the
agreed rate and target. Every accrual line records the invoice amount
that feeds the promise, and the totals on the contract show what has
been accrued, settled and what still remains to pay. A settlement marks
the period as closed with the paid amount, so the year-end conversation
starts from a figure the module already computed.

* A rebate contract per customer with period, rate and target amount.
* Accrual lines tied to the contract with invoice reference and value.
* Totals for accrued, settled and remaining amounts stored on the contract.
* A settlement action that closes the contract with a dated payout.
* One screen to review contracts and their accrual history together.
* Search filters for open and settled contracts.
* Validation that blocks negative amounts and bad date ranges.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'price': 89.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/rebate_contract_0_views.xml',
        'views/rebate_accrual_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
