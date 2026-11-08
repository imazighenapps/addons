# -*- coding: utf-8 -*-
{
    'name': 'FxRevalPro',
    'version': '18.0.1.0.0',
    'summary': 'Revalue open receivables and payables in a foreign currency at the closing rate, book the unrealized gain or loss in a balanced entry and keep the trail.',
    'description': '''FxRevalPro - Period-End Currency Revaluation
============================================
Closing the books with open receivables and payables in a foreign currency
is always the same uncomfortable exercise. The invoices were booked at the
rate of the day, the customer has not paid yet, and the balance sheet still
carries a value that no longer matches the market. Accountants rebuild the
calculation in a spreadsheet, forget one open item, and the unrealized
exchange difference lands in the profit and loss without any audit trail.

FxRevalPro performs the whole period-end revaluation inside Odoo. Pick the
foreign currency, enter the closing rate - one unit of that currency
expressed in your company currency - and the module scans every posted,
still open receivable and payable journal item in that currency. Each open
item becomes a revaluation line with its balance in the foreign currency,
its book value in the company currency, the new value at the closing rate
and the resulting unrealized gain or loss. Receivables that gain value and
debts that cost more are both handled with the right sign, and the totals
are summed per revaluation. When the figures look right, one click generates
a balanced journal entry in the chosen journal, with the gains and losses on
their own accounts and the counterpart on the partner receivable or payable
account. The document stays in draft until you decide to post it, can be
reset to draft, and every step is logged in the chatter.

* Scan of every open receivable and payable in one foreign currency.
* Closing rate entered as company-currency units per foreign unit.
* Book value, revalued balance and unrealized gain or loss per open item.
* Total gain, total loss and net unrealized result per revaluation.
* Balanced journal entry with dedicated gain and loss accounts.
* Draft and posted states, reset to draft, full chatter trail.
* Journal entry and rates frozen once the revaluation is posted.
* Multi-company, multi-currency, no Enterprise dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 99.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/fx_revaluation_0_views.xml',
        'views/fx_revaluation_line_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
