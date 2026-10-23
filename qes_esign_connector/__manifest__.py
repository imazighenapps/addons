# -*- coding: utf-8 -*-
{
    "name": "QES eSignature Connector",
    "version": "18.0.1.0.0",
    "summary": "eIDAS signing levels (SES/AdES/QES) with multi-provider framework: working demo provider plus Universign mapping.",
    "description": """
QES eSignature Connector
========================
Bring qualified electronic signatures to Odoo 18 Community: per-participant
signature levels (SES / AdES / QES), provider framework (working local demo
provider plus a real Universign REST mapping), envelope state machine,
hash-chained audit events, signed PDF retrieval and evidence export.
    """,
    "author": "Farid SLIMANI",
    "website": "https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI",
    "category": "Productivity",
    "license": "OPL-1",
    "price": 119.0,
    "currency": "EUR",
    "depends": ["base", "mail"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/providers.xml",
        "views/provider_views.xml",
        "views/envelope_views.xml",
        "views/document_views.xml",
        "views/event_views.xml",
        "views/menus.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": True,
    "auto_install": False,
}
