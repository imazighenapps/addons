# -*- coding: utf-8 -*-
{
    "name": "Expense Ocr",
    "version": "20.0.1.0.0",
    "category": "Productivity/Productivity",
    "summary": "Expense Ocr gives teams a focused Odoo app for expenses and OCR, with real-time visibility.",
    "author": "NORYVEX",
    "license": "OPL-1",
    "depends": ["hr_expense", "mail"],
    "data": [
        "security/ir.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "views/expense_ocr_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "support": "imazighenapps@gmail.com",
    "website": "imazighenapps@gmail.com",
    "price": 34.99,
    "currency": "EUR",
    "images": ['static/description/banner.png'],
    "description": "\nExpense Ocr\n===========\nExpense Ocr gives teams a focused Odoo app for expenses and OCR, with real-time visibility.\n\nFeatures:\n---------\n* Expenses\n* OCR\n* Dedicated workspace\n* Structured records\n* Workflow statuses\n* Role-based access\n* Grouped views\n\nIdeal for:\n----------\nBusiness teams, managers and administrators using Odoo.\n    "
}
