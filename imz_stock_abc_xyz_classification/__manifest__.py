# -*- coding: utf-8 -*-
{
    "name": "Imz Stock Abc Xyz Classification",
    "version": "18.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Give logistics teams a focused Odoo app for faster, error-free stock movements.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["stock", "sale", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/imz_stock_abc_xyz_classification_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
