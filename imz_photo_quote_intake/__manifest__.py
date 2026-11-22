# -*- coding: utf-8 -*-
{
    "name": "Photo Quote Intake",
    "version": "18.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Manage pipelines, customer follow-ups and sales performance with real-time visibility.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["crm", "sale", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/photo_quote_intake_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
