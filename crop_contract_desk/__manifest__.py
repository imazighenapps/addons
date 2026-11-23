# -*- coding: utf-8 -*-
{
    "name": "Crop Contract Desk",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Give purchasing teams full visibility over demand, prices and supplier performance.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["purchase", "stock", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/crop_contract_desk_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
