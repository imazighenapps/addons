# -*- coding: utf-8 -*-
{
    "name": "Customer Delivery Rules",
    "version": "18.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Control warehouse operations, lot traceability and inventory accuracy from one place.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["sale", "stock", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/customer_delivery_rules_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
