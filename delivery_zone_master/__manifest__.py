# -*- coding: utf-8 -*-
{
    "name": "Delivery Zone Master",
    "version": "20.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Give operations teams a clear Odoo workflow for deliveries, zone and master data, with full traceability.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "stock", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/delivery_zone_master_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nDelivery Zone Master\n====================\nGive operations teams a clear Odoo workflow for deliveries, zone and master data, with full traceability.\n\nFeatures:\n---------\n* Deliveries\n* Zone\n* Master data\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
