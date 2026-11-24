# -*- coding: utf-8 -*-
{
    "name": "Consolidated Project Invoice",
    "version": "20.0.1.0.0",
    "category": "Project/Project",
    "summary": "Centralize consolidated, projects and invoices in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "account", "project", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/consolidated_project_invoice_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nConsolidated Project Invoice\n============================\nCentralize consolidated, projects and invoices in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Consolidated\n* Projects\n* Invoices\n* Project workspace\n* Task tracking\n* Time and billing\n* Milestone planning\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
