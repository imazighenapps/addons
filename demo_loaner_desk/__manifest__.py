# -*- coding: utf-8 -*-
{
    "name": "Demo Loaner Desk",
    "version": "18.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Manage loaner from a single Odoo screen, with filters, follow-ups and reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "stock", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/demo_loaner_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nDemo Loaner Desk\n================\nManage loaner from a single Odoo screen, with filters, follow-ups and reporting.\n\nFeatures:\n---------\n* Loaner\n* Pipeline visibility\n* Fast quotations\n* Customer follow-ups\n* Pricing control\n* Renewal tracking\n* Full history\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
