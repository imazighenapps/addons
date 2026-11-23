# -*- coding: utf-8 -*-
{
    "name": "Notification Test Tool",
    "version": "19.0.1.0.0",
    "category": "Administration/Administration",
    "summary": "Extend Odoo safely with a production-ready, well-documented technical module.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/notification_test_tool_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
