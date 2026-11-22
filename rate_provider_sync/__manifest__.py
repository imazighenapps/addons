# -*- coding: utf-8 -*-
{
    "name": "Rate Provider Sync",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "summary": "Automate accounting controls, journal entries and financial reporting with full traceability.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/rate_provider_sync_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
