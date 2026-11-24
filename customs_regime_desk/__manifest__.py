# -*- coding: utf-8 -*-
{
    "name": "Customs Regime Desk",
    "version": "20.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Centralize customs and regime in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["stock", "account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/customs_regime_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nCustoms Regime Desk\n===================\nCentralize customs and regime in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Customs\n* Regime\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n* Grouped views\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
