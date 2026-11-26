# -*- coding: utf-8 -*-
{
    "name": "Financial Reports Community",
    "version": "18.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Build and print Profit & Loss, Balance Sheet, and custom financial reports from Odoo accounting data.",
    "description": """
Financial Reports Community
===========================
Create configurable financial report structures and generate period-based reports from posted accounting entries.

Key features
------------
* Report definitions with sections, account lines, and subtotals
* Profit & Loss, Balance Sheet, Cash Flow, Trial Balance, and custom report types
* Period comparison and account detail drill-down
* PDF export and CSV export
* Multi-company support
""",
    "author": "NORYVEX",
    "website": "https://noryvex.com",
    "support": "imazighenapps@gmail.com",
    "license": "OPL-1",
    "price": 129.0,
    "currency": "EUR",
    "depends": ["account"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/financial_report_views.xml",
        "views/financial_report_wizard_views.xml",
        "views/menus.xml",
        "report/financial_report_report.xml",
        "report/financial_report_templates.xml",
    ],
    "demo": [
        "data/demo.xml",
    ],
    "images": ["static/description/banner.png"],
    "application": True,
    "installable": True,
}
