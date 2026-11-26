# -*- coding: utf-8 -*-
{
    "name": "3PL Operations",
    "version": "20.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Manage third-party logistics contracts, stock statements, and billing from one Odoo workspace.",
    "description": """
3PL Operations
==============
A unified module for third-party logistics providers and their customers.

Key features
------------
* 3PL contracts with customer, warehouse, and billing rules
* Periodic stock statements with opening, inbound, outbound, and closing quantities
* Service billing lines based on storage, handling, and custom operations
* Portal-friendly customer visibility through shared statements
* Chatter tracking, multi-company support, and role-based access
""",
    "author": "NORYVEX",
    "website": "https://noryvex.com",
    "support": "imazighenapps@gmail.com",
    "license": "OPL-1",
    "price": 199.0,
    "currency": "EUR",
    "depends": ["stock", "account", "sale_management", "mail", "portal"],
    "data": [
        "security/security.xml",
        "security/ir.access.csv",
        "data/ir_sequence.xml",
        "views/contract_views.xml",
        "views/statement_views.xml",
        "views/menus.xml",
    ],
    "demo": ["data/demo.xml"],
    "images": ["static/description/banner.png"],
    "application": True,
    "installable": True,
}
