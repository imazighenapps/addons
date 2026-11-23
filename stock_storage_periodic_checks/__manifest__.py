# -*- coding: utf-8 -*-
{
    "name": "Stock Storage Periodic Checks",
    "version": "20.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Give logistics teams a focused Odoo app for faster, error-free stock movements.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["stock", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/stock_storage_periodic_checks_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
