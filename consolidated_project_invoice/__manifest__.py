# -*- coding: utf-8 -*-
{
    "name": "Consolidated Project Invoice",
    "version": "19.0.1.0.0",
    "category": "Project/Project",
    "summary": "Coordinate teams, milestones and deliverables with clear real-time progress.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["sale", "account", "project", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/consolidated_project_invoice_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
