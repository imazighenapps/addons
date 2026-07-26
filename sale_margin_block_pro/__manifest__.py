{
    "name": "Sales Margin Block PRO",
    "version": "19.0.1.0.0",
    "category": "Sales",
    "summary": "Block sale orders with low or negative margins using advanced rules",
    "description": """
Sales Margin Block PRO prevents the confirmation of sale orders when margins
do not meet defined profitability rules.

Main Features
-------------
- Automatic margin calculation on quotations (multi-currency aware)
- Block sale order confirmation when margin is too low
- Advanced margin rules by product, product template, category and customer
- Strictest-rule resolution when several lines/rules match an order
- Smart priority system (Product > Category > Customer > Global)
- Multi-company aware rules
- Manager override via dedicated security group, automatically granted to
  Sales Managers
- Full audit trail: every block and every override is logged and, when
  overridden, posted to the order's chatter
- Clear on-screen warning banner showing the current margin vs. the required
  minimum before the user even tries to confirm
- Clean and native Odoo interface

Designed for SMEs and sales-driven companies.
""",
    "author": "Farid SLIMANI",
    "license": "LGPL-3",
    "price": 99.0,
    "currency": "EUR",
    "depends": [
        "sale",
        "sale_management",
        "product",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/sale_order_view.xml",
        "views/margin_rule_view.xml",
        "views/margin_block_log_view.xml",
        "views/res_config_settings_view.xml",
    ],
    "images": [
        "static/description/banner.png",
    ],
    "installable": True,
    "application": False,
}
