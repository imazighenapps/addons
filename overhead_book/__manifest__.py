# -*- coding: utf-8 -*-
{
    "name": "Overhead Book",
    "version": "20.0.1.0.0",
    "category": "Project/Project",
    "summary": "Centralize overhead and bookings in one Odoo workspace, with role-based access and approvals.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["project", "analytic", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/overhead_book_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nOverhead Book\n=============\nCentralize overhead and bookings in one Odoo workspace, with role-based access and approvals.\n\nFeatures:\n---------\n* Overhead\n* Bookings\n* Project workspace\n* Task tracking\n* Time and billing\n* Milestone planning\n* Team coordination\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
