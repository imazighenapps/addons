# -*- coding: utf-8 -*-
{
    "name": "HACCP Food Safety Mini",
    "version": "18.0.1.0.0",
    "summary": "HACCP plans, CCP thresholds, temperature readings, allergens, DLC alerts, non-conformities.",
    "description": """
HACCP Food Safety Mini
======================
Food safety toolkit for small agri-food sites on Odoo 18 Community: HACCP
plans, critical control points with thresholds, temperature readings,
14 EU allergens on products, expiry alerts (DLC/DDM/FEFO) and
non-conformity workflow with withdrawal assistant.
    """,
    "author": "Farid SLIMANI",
    "website": "https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI",
    "category": "Industries",
    "license": "OPL-1",
    "price": 129.0,
    "currency": "EUR",
    "depends": ["base", "mail", "product", "stock", "uom", "product_expiry"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/plan_views.xml",
        "views/ccp_views.xml",
        "views/reading_views.xml",
        "views/nc_views.xml",
        "views/product_views.xml",
        "wizards/withdrawal_views.xml",
        "views/menus.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": True,
    "auto_install": False,
}
