# -*- coding: utf-8 -*-
{
    "name": "Pension Provision Desk",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Centralize pension and provisions in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/pension_provision_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nPension Provision Desk\n======================\nCentralize pension and provisions in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Pension\n* Provisions\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n* Export-ready reports\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
