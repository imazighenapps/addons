# -*- coding: utf-8 -*-
{
    "name": "Mrp Maintenance Windows",
    "version": "20.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Manage production orders, maintenance and time windows from a single Odoo screen, with filters, follow-ups and reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["mrp", "maintenance", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/mrp_maintenance_windows_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nMrp Maintenance Windows\n=======================\nManage production orders, maintenance and time windows from a single Odoo screen, with filters, follow-ups and reporting.\n\nFeatures:\n---------\n* Production orders\n* Maintenance\n* Time windows\n* Production planning\n* Work-order control\n* BOM accuracy\n* Cost tracking\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
