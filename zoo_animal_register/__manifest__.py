# -*- coding: utf-8 -*-
{
    "name": "Zoo Animal Register",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Centralize zoo, animal and registers in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["stock", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/zoo_animal_register_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nZoo Animal Register\n===================\nCentralize zoo, animal and registers in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Zoo\n* Animal\n* Registers\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
