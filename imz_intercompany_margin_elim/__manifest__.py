# -*- coding: utf-8 -*-
{
    "name": "Intercompany Margin Elim",
    "version": "18.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Centralize intercompany flows, margins and elim in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "stock", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/intercompany_margin_elim_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nIntercompany Margin Elim\n========================\nCentralize intercompany flows, margins and elim in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Intercompany flows\n* Margins\n* Elim\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
