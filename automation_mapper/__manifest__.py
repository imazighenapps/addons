# -*- coding: utf-8 -*-
{
    "name": "Automation Mapper",
    "version": "20.0.1.0.0",
    "category": "Administration/Administration",
    "summary": "Simplify administration, access control and technical maintenance inside Odoo.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/automation_mapper_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
