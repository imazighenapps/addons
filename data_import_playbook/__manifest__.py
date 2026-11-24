# -*- coding: utf-8 -*-
{
    "name": "Data Import Playbook",
    "version": "20.0.1.0.0",
    "category": "Administration/Administration",
    "summary": "Manage data quality, imports and playbook from a single Odoo screen, with filters, follow-ups and reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/data_import_playbook_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nData Import Playbook\n====================\nManage data quality, imports and playbook from a single Odoo screen, with filters, follow-ups and reporting.\n\nFeatures:\n---------\n* Data quality\n* Imports\n* Playbook\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
