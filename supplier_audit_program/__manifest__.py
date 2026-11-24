# -*- coding: utf-8 -*-
{
    "name": "Supplier Audit Program",
    "version": "20.0.1.0.0",
    "category": "Purchase/Purchase",
    "summary": "Supplier Audit Program: manage supplier records, audit trails and programs in Odoo, with clear statuses and full traceability.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["purchase", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/supplier_audit_program_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 59.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nSupplier Audit Program\n======================\nSupplier Audit Program: manage supplier records, audit trails and programs in Odoo, with clear statuses and full traceability.\n\nFeatures:\n---------\n* Supplier records\n* Audit trails\n* Programs\n* Purchase approvals\n* Cost control\n* Receipt visibility\n* Vendor comparison\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
