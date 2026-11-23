# -*- coding: utf-8 -*-
{
    "name": "Project Portal",
    "version": "18.0.1.0.0",
    "category": "Project/Project",
    "summary": "Coordinate teams, milestones and deliverables with clear real-time progress.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["project", "portal", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/project_portal_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
