# -*- coding: utf-8 -*-
{
    "name": "RMA Returns Portal Pro",
    "version": "20.0.1.0.0",
    "summary": "Self-service returns portal, RMA approval, QC grading, refunds and second life.",
    "description": """
RMA Returns Portal Pro
======================
Complete returns management for Odoo 20 Community e-commerce: customer
self-service portal, eligibility engine (withdrawal vs warranty), RMA
numbering and approval, return labels, reception in quarantine, QC grading
(A/B/C/D), refunds via credit notes, exchanges and second-life resale.
    """,
    "author": "Farid SLIMANI",
    "website": "https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI",
    "category": "Website",
    "license": "OPL-1",
    "price": 99.0,
    "currency": "EUR",
    "depends": ["base", "mail", "product", "sale", "sale_stock", "stock", "website", "portal", "account"],
    "data": [
        "security/security.xml",
        "security/ir.access.csv",
        "data/sequence.xml",
        "views/reason_views.xml",
        "views/request_views.xml",
        "views/config_views.xml",
        "views/product_views.xml",
        "views/menus.xml",
        "views/portal_templates.xml",
        "report/return_label.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": True,
    "auto_install": False,
}
