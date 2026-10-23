# -*- coding: utf-8 -*-
{
    "name": "Documents Storage Saver",
    "version": "19.0.1.0.0",
    "summary": "Find duplicate, orphan and oversized attachments to reclaim storage safely.",
    "description": """
Documents Storage Saver
=======================
Reclaim Odoo storage in minutes: duplicate detection by content hash with
safe review-and-delete, orphan attachments detection (linked to deleted
records), oversized files report and a storage dashboard. Manager-only
deletion with dry-run first.
    """,
    "author": "Farid SLIMANI",
    "website": "https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI",
    "category": "Document Management",
    "license": "OPL-1",
    "price": 49.0,
    "currency": "EUR",
    "depends": ["base", "mail"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/scan_views.xml",
        "views/duplicate_views.xml",
        "views/orphan_views.xml",
        "views/menus.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": False,
    "auto_install": False,
}
