# -*- coding: utf-8 -*-
{
    "name": "Periodic Recontact Plan",
    "version": "19.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Manage pipelines, customer follow-ups and sales performance with real-time visibility.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["crm", "sale", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/periodic_recontact_plan_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
