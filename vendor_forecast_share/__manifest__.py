# -*- coding: utf-8 -*-
{
    "name": "Vendor Forecast Share",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Centralize vendor records, forecasts and sharing in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["purchase", "sale", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/vendor_forecast_share_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nVendor Forecast Share\n=====================\nCentralize vendor records, forecasts and sharing in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Vendor records\n* Forecasts\n* Sharing\n* Supplier records\n* Purchase approvals\n* Cost control\n* Receipt visibility\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
