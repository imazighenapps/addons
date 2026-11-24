# -*- coding: utf-8 -*-
{
    "name": "Mrp Cost Variance Analysis",
    "version": "20.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Centralize production orders, cost tracking and variances in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["mrp", "account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/mrp_cost_variance_analysis_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nMrp Cost Variance Analysis\n==========================\nCentralize production orders, cost tracking and variances in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Production orders\n* Cost tracking\n* Variances\n* Production planning\n* Work-order control\n* BOM accuracy\n* Quality checks\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
