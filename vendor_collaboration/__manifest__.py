# -*- coding: utf-8 -*-
{
    "name": "Vendor Collaboration",
    "version": "19.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Collaborate with vendors on ASNs, chargebacks, and catalog updates from one Odoo workspace.",
    "description": """
Vendor Collaboration
====================
A unified vendor collaboration workspace for purchasing teams.

Key features
------------
* Advanced Shipping Notices (ASN) linked to purchase orders and receipts
* Vendor chargeback tracking with amounts, reasons, and resolution workflow
* Vendor catalog items with pricing, lead times, and validity
* Chatter tracking, role-based access, and multi-company support
""",
    "author": "NORYVEX",
    "website": "https://noryvex.com",
    "support": "imazighenapps@gmail.com",
    "license": "OPL-1",
    "price": 179.0,
    "currency": "EUR",
    "depends": ["purchase", "stock", "account", "mail"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "views/vendor_asn_views.xml",
        "views/vendor_chargeback_views.xml",
        "views/vendor_catalog_views.xml",
        "views/menus.xml",
    ],
    "demo": ["data/demo.xml"],
    "images": ["static/description/banner.png"],
    "application": True,
    "installable": True,
}
