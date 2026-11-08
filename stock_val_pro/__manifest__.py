# -*- coding: utf-8 -*-
{
    'name': 'StockValPro',
    'version': '18.0.1.0.0',
    'summary': 'Month-end stock valuation per product from done moves, valued at cost, with totals, slow movers and a confirm lock for the closing file.',
    'description': '''StockValPro - Stock Valuation Report for Month-End Closing
==========================================================
Inventory is the line of the balance sheet that everybody trusts and
nobody can prove. At closing, someone exports every stock move of the
period, someone else retypes the cost of each product, and the two files
still disagree on the last day. The auditor asks for the detail behind
the total, and the detail has already been overwritten by the next
receipt.

StockValPro rebuilds the valuation inside Odoo, from the only source that
matters: the done stock moves. Pick a period, optionally narrow it to one
internal location, and the module aggregates every move into a single
line per product. Inbound and outbound quantities are valued at the
product standard cost read at generation time and stored on the line, so
the report does not move when a cost is updated next week. Balances,
totals per report and slow movers are computed for you, the report can be
confirmed to freeze it for the closing file, and the chatter keeps the
story of who generated and who locked it. Each line keeps the product,
its category, the quantities in and out and the cost that was used, so
the detail is still there when the auditor comes back. Closing becomes a
five-minute check instead of a spreadsheet archaeology project.

* One valuation line per product for any closing period.
* Inbound and outbound quantities from done stock moves only.
* Values frozen at the standard cost of the generation date.
* Net balance quantity and net balance value per product.
* Totals per report, ready for the inventory account reconciliation.
* Automatic slow mover flag for products received but never issued.
* Draft and confirmed states, locked once confirmed.
* Multi-company, optional location filter, no Enterprise dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Inventory',
    'license': 'OPL-1',
    'price': 129.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'stock',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/stock_val_report_0_views.xml',
        'views/stock_val_report_line_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
