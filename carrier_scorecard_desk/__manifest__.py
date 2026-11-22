# -*- coding: utf-8 -*-
{
    "name": "Carrier Scorecard Desk",
    "version": "18.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Control warehouse operations, lot traceability and inventory accuracy from one place.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["stock", "sale", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/carrier_scorecard_desk_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
