# -*- coding: utf-8 -*-
{
    "name": "Vat Cash Basis Desk",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "summary": "Track VAT controls, cash and basis in a dedicated Odoo workspace, from intake to reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/vat_cash_basis_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 59.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nVat Cash Basis Desk\n===================\nTrack VAT controls, cash and basis in a dedicated Odoo workspace, from intake to reporting.\n\nFeatures:\n---------\n* VAT controls\n* Cash\n* Basis\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
