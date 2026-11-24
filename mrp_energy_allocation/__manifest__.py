# -*- coding: utf-8 -*-
{
    "name": "Mrp Energy Allocation",
    "version": "20.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Give operations teams a clear Odoo workflow for production orders, energy and allocation, with full traceability.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["mrp", "account", "maintenance", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/mrp_energy_allocation_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nMrp Energy Allocation\n=====================\nGive operations teams a clear Odoo workflow for production orders, energy and allocation, with full traceability.\n\nFeatures:\n---------\n* Production orders\n* Energy\n* Allocation\n* Production planning\n* Work-order control\n* BOM accuracy\n* Cost tracking\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
