# -*- coding: utf-8 -*-
{
    "name": "Po Dispute Desk",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Po Dispute Desk keeps purchase orders and dispute under control in Odoo, with workflow statuses and exports.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["purchase", "account", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/po_dispute_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nPo Dispute Desk\n===============\nPo Dispute Desk keeps purchase orders and dispute under control in Odoo, with workflow statuses and exports.\n\nFeatures:\n---------\n* Purchase orders\n* Dispute\n* Supplier records\n* Purchase approvals\n* Cost control\n* Receipt visibility\n* Vendor comparison\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
