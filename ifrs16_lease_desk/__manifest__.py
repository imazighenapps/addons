# -*- coding: utf-8 -*-
{
    "name": "Ifrs Lease Desk",
    "version": "19.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Ifrs Lease Desk keeps ifrs16 and lease under control in Odoo, with workflow statuses and exports.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/ifrs16_lease_desk_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nIfrs Lease Desk\n===============\nIfrs Lease Desk keeps ifrs16 and lease under control in Odoo, with workflow statuses and exports.\n\nFeatures:\n---------\n* Ifrs16\n* Lease\n* Audit-ready entries\n* Variance tracking\n* Reconciliation workspace\n* Role-based access\n* Export-ready reports\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
