# -*- coding: utf-8 -*-
{
    "name": "Ppv Analytics Desk",
    "version": "18.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Give purchasing teams full visibility over demand, prices and supplier performance.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["purchase", "account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/ppv_analytics_desk_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
