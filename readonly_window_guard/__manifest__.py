# -*- coding: utf-8 -*-
{
    "name": "Readonly Window Guard",
    "version": "20.0.1.0.0",
    "category": "Administration/Administration",
    "summary": "Manage readonly, window and guardrails from a single Odoo screen, with filters, follow-ups and reporting.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/readonly_window_guard_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nReadonly Window Guard\n=====================\nManage readonly, window and guardrails from a single Odoo screen, with filters, follow-ups and reporting.\n\nFeatures:\n---------\n* Readonly\n* Window\n* Guardrails\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
