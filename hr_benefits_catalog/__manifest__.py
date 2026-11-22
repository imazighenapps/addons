# -*- coding: utf-8 -*-
{
    "name": "Hr Benefits Catalog",
    "version": "19.0.1.0.0",
    "category": "Human Resources/Human Resources",
    "summary": "Centralize employee records, contracts and HR workflows in one secure Odoo app.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["hr", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/hr_benefits_catalog_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
