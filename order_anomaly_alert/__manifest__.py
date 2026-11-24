# -*- coding: utf-8 -*-
{
    "name": "Order Anomaly Alert",
    "version": "20.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Centralize orders, anomaly detection and alerts in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/order_anomaly_alert_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nOrder Anomaly Alert\n===================\nCentralize orders, anomaly detection and alerts in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Orders\n* Anomaly detection\n* Alerts\n* Pipeline visibility\n* Fast quotations\n* Customer follow-ups\n* Pricing control\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
