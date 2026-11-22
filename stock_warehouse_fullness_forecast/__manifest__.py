# -*- coding: utf-8 -*-
{
    "name": "Stock Warehouse Fullness Forecast",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Give logistics teams a focused Odoo app for faster, error-free stock movements.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["stock", "purchase", "sale", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/stock_warehouse_fullness_forecast_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
