# -*- coding: utf-8 -*-
{
    "name": "Supplier File Completeness",
    "version": "19.0.1.0.0",
    "summary": "Track mandatory supplier documents, expiry dates and payment blocking.",
    "description": """
Supplier File Completeness
==========================
Never pay a supplier whose file is incomplete: required document register
(extraction, insurance, bank details, vigilance attestation), expiry alerts,
completeness scoring and an optional hard block on vendor bills.
    """,
    "author": "Farid SLIMANI",
    "website": "https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI",
    "category": "Purchases",
    "license": "OPL-1",
    "price": 79.0,
    "currency": "EUR",
    "depends": ["base", "mail", "purchase"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/document_types.xml",
        "views/type_views.xml",
        "views/document_views.xml",
        "views/status_views.xml",
        "views/partner_views.xml",
        "views/menus.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": False,
    "auto_install": False,
}