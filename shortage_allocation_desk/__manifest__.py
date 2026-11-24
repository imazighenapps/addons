# -*- coding: utf-8 -*-
{
    "name": "Shortage Allocation Desk",
    "version": "20.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Centralize shortages and allocation in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["stock", "sale", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/shortage_allocation_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nShortage Allocation Desk\n========================\nCentralize shortages and allocation in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Shortages\n* Allocation\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n* Grouped views\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
