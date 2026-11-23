# -*- coding: utf-8 -*-
{
    "name": "Billing Schedule",
    "version": "18.0.1.0.0",
    "category": "Project/Project",
    "summary": "Coordinate teams, milestones and deliverables with clear real-time progress.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["sale", "project", "account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/billing_schedule_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
