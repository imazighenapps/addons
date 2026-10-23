# -*- coding: utf-8 -*-
{
    "name": "REP & PPWR Packaging Tracker",
    "version": "18.0.1.0.0",
    "summary": "French REP declarations and EU PPWR readiness: materials, tariffs, packaging costs, deposits.",
    "description": """
REP & PPWR Packaging Tracker
============================
Track packaging placed on the market for French EPR (REP) declarations
(Citeo, Leko, Citeo Pro, Leko Pro, Twiice) and prepare EU PPWR compliance:
material referential with tariffs, product packaging sheets, automatic cost
computation on deliveries, declaration register with CSV export, deposit
management and recyclability scoring.
    """,
    "author": "Farid SLIMANI",
    "website": "https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI",
    "category": "Inventory",
    "license": "OPL-1",
    "price": 79.0,
    "currency": "EUR",
    "depends": ["base", "mail", "product", "sale", "stock"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "data/materials.xml",
        "views/material_views.xml",
        "views/packaging_views.xml",
        "views/ledger_views.xml",
        "views/declaration_views.xml",
        "views/deposit_views.xml",
        "views/product_views.xml",
        "views/menus.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": True,
    "auto_install": False,
}
