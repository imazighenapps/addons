# -*- coding: utf-8 -*-
{
    'name': 'ReorderForecast',
    'version': '20.0.1.0.0',
    'summary': 'Turn real outgoing consumption into reorder suggestions: average daily issue, stock on hand, incoming quantities and a suggested purchase quantity per product and location.',
    'description': '''ReorderForecast - Consumption-Based Reorder Suggestions
======================================================
Reorder points set once and never reviewed either overstock slow movers or
run out of fast ones. The signal is already in the warehouse: what actually
left the stock over the last weeks.

ReorderForecast reads done outgoing moves over a lookback window, computes the
average daily issue per product and location, subtracts stock on hand and
incoming quantities, and proposes a quantity to cover a chosen horizon.

* Lookback window, horizon and location chosen at each run.
* Average daily issue computed from done outgoing moves.
* Stock on hand and incoming quantities taken into account.
* One open suggestion per product and location, refreshed on each run.
* Suggestions marked ordered, ignored or reopened.
* Category filter to focus on a product family.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Inventory',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'stock',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/stock_reorder_suggestion_0_views.xml',
        'views/stock_reorder_forecast_1_views.xml',
        'views/menus.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
