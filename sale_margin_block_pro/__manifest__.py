{
    "name": "Sales Margin Block PRO",
    "version": "18.0.1.0.1",
    "category": "Sales",
    "summary": "Block sale orders with low or negative margins using advanced rules",
    "description": """
Sales Margin Block PRO prevents the confirmation of sale orders when margins
do not meet defined profitability rules.

Main Features:
- Automatic margin calculation on quotations
- Block sale order confirmation when margin is too low
- Advanced margin rules by product, category and customer
- Smart priority system (Product > Category > Customer > Global)
- Manager override via security group
- Clean and native Odoo interface

Designed for SMEs and sales-driven companies.
""",
    "author": "Farid SLIMANI",
    "license": "LGPL-3",
    "price": 79.0,
    "currency": "EUR",
    "depends": [
        "sale",
        "sale_management",
        "product"
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/sale_order_view.xml",
        "views/margin_rule_view.xml",
        "views/res_config_settings_view.xml"
    ],
    "images": [
        "static/description/banner.png"
    ],
    "installable": True,
    "application": False,
}
