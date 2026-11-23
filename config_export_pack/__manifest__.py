# -*- coding: utf-8 -*-
{
    "name": "Config Export Pack",
    "version": "20.0.1.0.0",
    "category": "Administration/Administration",
    "summary": "Extend Odoo safely with a production-ready, well-documented technical module.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/config_export_pack_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
