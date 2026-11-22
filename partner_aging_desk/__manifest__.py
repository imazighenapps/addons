# -*- coding: utf-8 -*-
{
    "name": "Partner Aging Desk",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "summary": "Reconcile accounts, monitor balances and audit every financial entry from one Odoo workspace.",
    "description": """Tableaux d'aging clients (AR) et fournisseurs (AP) par tranches,
engagement par tranche, actions recommandées, suivi DSO/DPO et exports.""",
    "author": "ImazighenApps",
    "website": "https://apps.odoo.com/",
    "license": "LGPL-3",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/aging_views.xml",
        "views/menus.xml",
        "report/aging_report.xml",
    ],
    "application": False,
}
