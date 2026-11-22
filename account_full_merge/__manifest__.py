# -*- coding: utf-8 -*-
{
    "name": "Account Full Merge",
    "version": "19.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Manage pipelines, customer follow-ups and sales performance with real-time visibility.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["account", "sale", "crm", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/account_full_merge_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
