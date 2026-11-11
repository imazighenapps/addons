# -*- coding: utf-8 -*-
{
    'name': 'VATCross',
    'version': '18.0.1.0.0',
    'summary': 'Cross-check the VAT report against the underlying journal entries and explain the differences before filing.',
    'description': '''VATCross - File What You Verified
=================================
A VAT return is only as good as the boxes behind it. The report says one
figure, the journal entries say another, and the difference is usually
found the day after filing, when it is already expensive. Reconciling the
two means copying numbers into a spreadsheet and writing the explanation
in an email nobody can find later.

VATCross keeps a cross-check per period in Odoo: you declare the amount
reported in each VAT box and the amount you recomputed from the journal
entries, and the difference is computed and stored for you. Every line
carries the explanation of the gap and can be marked as justified once
reviewed, so nothing is filed blind. A differences screen lists only the
boxes that still need attention, and closing the check freezes a dated
record of what was verified. The return you file is the return you can
defend.

* A VAT cross-check per period with a clear filing status.
* One line per VAT box with reported and ledger amounts.
* The difference computed and stored on every line.
* A justification and a reviewed flag on each difference.
* One screen for every box that still differs or awaits review.
* The check closes only when every line is reviewed.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
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
        'views/vat_check_0_views.xml',
        'views/vat_check_line_1_views.xml',
        'views/vat_difference_2_views.xml',
        'views/menus.xml',
        'views/vat_difference_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
