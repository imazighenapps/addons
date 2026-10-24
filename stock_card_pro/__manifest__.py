# -*- coding: utf-8 -*-
{
    'name': 'StockCard Pro - Valued Stock Card',
    'version': '18.0.1.0.0',
    'summary': 'Audit-ready stock card per product, warehouse and lot: opening, inbound, outbound, closing quantity and value, with PDF.',
    'description': '''StockCard Pro - Valued Stock Card
=================================
The stock card your accountant and your auditor keep asking for, in one click.

Choose a product, a warehouse and a period. StockCard Pro rebuilds the full
movement history from done stock moves: opening quantity, every inbound and
outbound, closing quantity, and the value at cost. The PDF is ready for the
audit file.

* Stock card per product, per warehouse and per lot or serial number.
* Opening quantity computed from history, not from the current stock.
* Inbound and outbound movements with reference, partner and date.
* Closing quantity and closing value at cost.
* Professional PDF with company layout.
* Multi-company.
* Full traceability: every line links back to the stock move.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Inventory/Inventory',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'stock',
        'product',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/stock_card_0_views.xml',
        'views/menus.xml',
        'report/stock_card_report.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
