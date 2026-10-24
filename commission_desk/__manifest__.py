# -*- coding: utf-8 -*-
{
    "name": "CommissionDesk — Sales Commission Engine",
    "version": "18.0.1.0.0",
    "summary": "Calculate, validate and pay sales commissions from orders, invoices and payments, with automatic clawback.",
    "description": """
CommissionDesk — Sales Commission Engine
========================================
Stop calculating sales commissions in spreadsheets.

CommissionDesk turns Odoo orders, invoices and payments into clear,
auditable commission lines. Define your rules once, generate a monthly
statement in one click, validate it, and pay the right amount every time.

* Commission rules by salesperson, team, customer, product category or margin.
* Three calculation bases: confirmed order, posted invoice, registered payment.
* Percentage or fixed amount, with volume tiers.
* Monthly statement per salesperson, PDF and portal ready.
* Validation workflow: sales manager, then finance.
* Automatic clawback on credit notes and unpaid invoices.
* Multi-currency and multi-company.
* Full audit trail and CSV / SEPA export.
    """,
    "author": "Farid SLIMANI",
    "website": "https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI",
    "category": "Sales/Sales",
    "license": "OPL-1",
    "price": 89.0,
    "currency": "EUR",
    "depends": ["base", "mail", "sale", "account", "crm"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/commission_views.xml",
        "views/sale_order_views.xml",
        "views/menus.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": False,
    "auto_install": False,
}
