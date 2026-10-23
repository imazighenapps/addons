# -*- coding: utf-8 -*-
{
    "name": "QR Pay Pro",
    "version": "19.0.1.0.0",
    "summary": "Payment QR premium layer: RF/SCOR auto-references, QRR counter, compliance cockpit, camt import.",
    "description": """
QR Pay Pro
==========
Premium layer on top of native Odoo QR codes (EPC + Swiss): automatic RF
creditor references (ISO 11649), dedicated Swiss QRR counter with mod10r
control, EPC purpose codes, compliance cockpit with one-click fixes, QR on
more documents and camt.053 import with QR payload decoding.
    """,
    "author": "Farid SLIMANI",
    "website": "https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI",
    "category": "Accounting",
    "license": "OPL-1",
    "price": 69.0,
    "currency": "EUR",
    "depends": ["base", "account", "account_qr_code_sepa"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/move_views.xml",
        "views/menus.xml",
        "wizards/camt_views.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": False,
    "auto_install": False,
}
