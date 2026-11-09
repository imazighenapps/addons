# -*- coding: utf-8 -*-
{
    'name': 'ProductQuality',
    'version': '18.0.1.0.0',
    'summary': 'Score every product sheet against your own completeness rules, list the missing barcodes, weights, costs and categories, and watch the score improve scan after scan.',
    'description': '''ProductQuality - Clean Product Master Data
==========================================
A missing barcode stops the scanner at the packing station. A product
created without a cost makes every margin report wrong. A sale price left
at zero slips into a quotation and nobody notices before the customer
signs it.

ProductQuality scores the master data instead of hoping it is clean.
Define your own completeness rules - barcode, weight, cost, sale price,
category, sales description - give each one a severity and a weight in
points, then run a scan. Every active product of the company is checked
against the rules, one anomaly line is created per missing field with a
readable message, and the scan receives a score from 0 to 100 weighted by
the points of each rule. Run the scan again after cleaning the data: the
same scope, the same rules, no duplicate line. Each anomaly can be marked
as fixed or ignored, and the graph and pivot views show where the master
data is still weak.

* Completeness rules with a severity and a weight in points.
* One scan checks every active product of the company.
* One anomaly line per missing field, with a readable message.
* A 0-100 score weighted by the points of each rule.
* Idempotent runs: no duplicate line when the scan is replayed.
* An optional scope to scan a single product or a short list.
* Anomalies followed as new, fixed or ignored.
* List, form, search, graph and pivot, multi-company isolation.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Inventory',
    'license': 'OPL-1',
    'price': 79.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'product',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/product_quality_scan_0_views.xml',
        'views/product_quality_line_1_views.xml',
        'views/product_quality_rule_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
