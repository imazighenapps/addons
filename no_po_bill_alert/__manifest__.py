# -*- coding: utf-8 -*-
{
    "name": "No Po Bill Alert",
    "version": "18.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Give operations teams a clear Odoo workflow for purchase orders, bills and alerts, with full traceability.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "purchase", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/no_po_bill_alert_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nNo Po Bill Alert\n================\nGive operations teams a clear Odoo workflow for purchase orders, bills and alerts, with full traceability.\n\nFeatures:\n---------\n* Purchase orders\n* Bills\n* Alerts\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
