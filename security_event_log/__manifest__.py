# -*- coding: utf-8 -*-
{
    "name": "Security Event Log",
    "version": "20.0.1.0.0",
    "category": "Administration/Administration",
    "summary": "Run security, events and activity history end to end in Odoo, with structured records and audit-ready history.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/security_event_log_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nSecurity Event Log\n==================\nRun security, events and activity history end to end in Odoo, with structured records and audit-ready history.\n\nFeatures:\n---------\n* Security\n* Events\n* Activity history\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
