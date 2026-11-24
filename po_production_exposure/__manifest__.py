# -*- coding: utf-8 -*-
{
    "name": "Po Production Exposure",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Give operations teams a clear Odoo workflow for purchase orders, production and exposure, with full traceability.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["purchase", "mrp", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/po_production_exposure_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nPo Production Exposure\n======================\nGive operations teams a clear Odoo workflow for purchase orders, production and exposure, with full traceability.\n\nFeatures:\n---------\n* Purchase orders\n* Production\n* Exposure\n* Supplier records\n* Purchase approvals\n* Cost control\n* Receipt visibility\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
