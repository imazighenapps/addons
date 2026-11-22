# -*- coding: utf-8 -*-
{
    "name": "Customer Group Pooling",
    "version": "18.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Give sales teams a focused Odoo app to convert opportunities into recurring revenue.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["account", "sale", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/customer_group_pooling_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
