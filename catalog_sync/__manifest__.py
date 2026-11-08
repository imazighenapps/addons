# -*- coding: utf-8 -*-
{
    'name': 'CatalogSync',
    'version': '20.0.1.0.0',
    'summary': 'Paste a supplier price list, match products by reference, simulate the new cost and sale price with your margin rule, then apply the update with a full history.',
    'description': '''CatalogSync - Supplier Price Updates
====================================
The supplier sends a new price list twice a year, as a spreadsheet with two
columns. Somebody opens the product form of each reference, one by one, and
retypes the cost - and the sale price is either forgotten or updated with a
margin nobody can reproduce. Two weeks later, half the catalogue is wrong.

CatalogSync takes the pasted list, matches every reference to a product by
its internal reference or by the supplier's own code, and builds a
simulation: the cost before, the cost after, the sale price before and the
sale price after, computed with the margin rule of the product category.
Nothing is written before you press Apply, and the lines that found no
product stay visible as unmatched, so the list itself becomes the control.
Each update is kept as a dated batch with its totals and its history.

* Paste a list in the form "reference;price", tab or space separated.
* Match by internal reference or by the supplier product code.
* Simulation of old and new cost, old and new sale price.
* Margin rules by product category, with a generic fallback.
* Rounding step and option to leave the sale price untouched.
* Unmatched references kept visible before anything is applied.
* Apply in one click, with a dated batch and full history.
* Graph and pivot by category and by supplier, multi-company isolation.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Purchases/Purchases',
    'license': 'OPL-1',
    'price': 79.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'purchase',
        'product',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/catalog_import_0_views.xml',
        'views/catalog_import_line_1_views.xml',
        'views/catalog_margin_rule_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
