# -*- coding: utf-8 -*-
{
    "name": "Brute Force Lockout",
    "version": "20.0.1.0.0",
    "category": "Administration/Administration",
    "summary": "Give operations teams a clear Odoo workflow for brute, force and lockout, with full traceability.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/brute_force_lockout_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nBrute Force Lockout\n===================\nGive operations teams a clear Odoo workflow for brute, force and lockout, with full traceability.\n\nFeatures:\n---------\n* Brute\n* Force\n* Lockout\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
