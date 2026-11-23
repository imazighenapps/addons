# -*- coding: utf-8 -*-
{
    "name": "Hr Candidate Sla",
    "version": "18.0.1.0.0",
    "category": "Human Resources/Human Resources",
    "summary": "Centralize employee records, contracts and HR workflows in one secure Odoo app.",
    "author": "ImazighenApps",
    "license": "LGPL-3",
    "depends": ["hr_recruitment", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/hr_candidate_sla_views.xml",
        "views/menus.xml",
    ],
    "application": False,
}
