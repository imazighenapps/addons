# -*- coding: utf-8 -*-
{
    "name": "Publish Manuscript Flow",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Centralize publish, manuscript and workflows in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "project", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/publish_manuscript_flow_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nPublish Manuscript Flow\n=======================\nCentralize publish, manuscript and workflows in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Publish\n* Manuscript\n* Workflows\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
