# -*- coding: utf-8 -*-
{
    "name": "Mrp Machine Hour Rates",
    "version": "20.0.1.0.0",
    "category": "Manufacturing/Manufacturing",
    "summary": "Track production orders, machine data and hourly rates in a dedicated Odoo workspace, from intake to reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["mrp", "maintenance", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/mrp_machine_hour_rates_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nMrp Machine Hour Rates\n======================\nTrack production orders, machine data and hourly rates in a dedicated Odoo workspace, from intake to reporting.\n\nFeatures:\n---------\n* Production orders\n* Machine data\n* Hourly rates\n* Production planning\n* Work-order control\n* BOM accuracy\n* Cost tracking\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
