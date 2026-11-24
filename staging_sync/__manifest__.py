# -*- coding: utf-8 -*-
{
    "name": "Staging Sync",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Centralize staging environments and synchronization in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/staging_sync_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nStaging Sync\n============\nCentralize staging environments and synchronization in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Staging environments\n* Synchronization\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n* Grouped views\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
