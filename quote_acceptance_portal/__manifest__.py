# -*- coding: utf-8 -*-
{
    "name": "Quote Acceptance Portal",
    "version": "19.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Qualify leads, accelerate quotations and close more deals from a single Odoo workspace.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["sale", "portal", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/quote_acceptance_portal_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
