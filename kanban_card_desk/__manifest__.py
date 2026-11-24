# -*- coding: utf-8 -*-
{
    "name": "Kanban Card Desk",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Kanban Card Desk gives teams a focused Odoo app for kanban boards and cards, with real-time visibility.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["stock", "purchase", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/kanban_card_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nKanban Card Desk\n================\nKanban Card Desk gives teams a focused Odoo app for kanban boards and cards, with real-time visibility.\n\nFeatures:\n---------\n* Kanban boards\n* Cards\n* Supplier records\n* Purchase approvals\n* Cost control\n* Receipt visibility\n* Vendor comparison\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
