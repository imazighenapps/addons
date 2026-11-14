# -*- coding: utf-8 -*-
{
    'name': 'ScanPack Desk',
    'version': '18.0.1.0.0',
    'summary': 'Validate pickings by barcode scan: accepted scans are logged, unexpected barcodes are refused, and validation stays blocked while prepared differs from requested, unless a manager grants a reason-tracked exception.',
    'description': '''ScanPack Desk - Barcode Pick Validation
=======================================
A picker packs an order without proving that the physical items match the
order. One wrong item costs the full round trip - two shipments, two
collections - and an unhappy customer. In Odoo Community the Validate
button never checks the physical preparation, and the guided barcode
screen is an Enterprise app.

ScanPack Desk turns every picking into a guided scan screen for a
keyboard-wedge (HID) reader. Open the scan session of a picking, scan the
product barcode or internal reference: the prepared quantity of the right
pick line grows by one, and the totals update live. A barcode that does
not belong to the pick order is refused and written to the scan journal
with the user, the time and the reason. Validation stays blocked while
prepared differs from requested: a warehouse manager can grant an
exception with a reason, which is also written to the journal, and the
picking validates with the documented gap. Nothing is silently skipped.

* One scan field per picking: scan product barcode or internal reference.
* Accepted scans grow the prepared quantity of the exact pick line.
* Unexpected barcodes are refused and logged, never silently ignored.
* Validation blocked while prepared does not match requested.
* Manager exception with a mandatory reason, written to the journal.
* Immutable scan journal per picking: who scanned what, when, and why.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Inventory',
    'license': 'OPL-1',
    'price': 99.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'stock',
        'product',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/scan_session_0_views.xml',
        'views/scan_move_1_views.xml',
        'views/scan_log_2_views.xml',
        'views/menus.xml',
        'views/stock_picking_views.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
