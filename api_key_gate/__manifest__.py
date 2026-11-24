# -*- coding: utf-8 -*-
{
    "name": "Api Key Gate",
    "version": "20.0.1.0.0",
    "category": "Administration/Administration",
    "summary": "Centralize api, key and approval gates in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/api_key_gate_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nApi Key Gate\n============\nCentralize api, key and approval gates in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Api\n* Key\n* Approval gates\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
