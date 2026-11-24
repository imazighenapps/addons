# -*- coding: utf-8 -*-
{
    "name": "Invoice Quote Conformity",
    "version": "18.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Invoice Quote Conformity keeps invoices, quotations and conformity under control in Odoo, with workflow statuses and exports.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["sale", "account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/invoice_quote_conformity_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nInvoice Quote Conformity\n========================\nInvoice Quote Conformity keeps invoices, quotations and conformity under control in Odoo, with workflow statuses and exports.\n\nFeatures:\n---------\n* Invoices\n* Quotations\n* Conformity\n* Pipeline visibility\n* Fast quotations\n* Customer follow-ups\n* Pricing control\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
