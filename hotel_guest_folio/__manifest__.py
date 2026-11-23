# -*- coding: utf-8 -*-
{
    "name": "Hotel Guest Folio",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Organize daily work, approvals and documents in a focused Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["sale", "account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/hotel_guest_folio_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
