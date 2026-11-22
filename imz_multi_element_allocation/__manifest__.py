# -*- coding: utf-8 -*-
{
    "name": "Multi Element Allocation",
    "version": "20.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Automate accounting controls, journal entries and financial reporting with full traceability.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["account", "sale", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/multi_element_allocation_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
