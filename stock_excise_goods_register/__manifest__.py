# -*- coding: utf-8 -*-
{
    "name": "Stock Excise Goods Register",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Give logistics teams a focused Odoo app for faster, error-free stock movements.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["stock", "account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/stock_excise_goods_register_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
