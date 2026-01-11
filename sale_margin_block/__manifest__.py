{
    "name": "Sales Margin Block",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "summary": "Block sale order confirmation if margin is too low",
    "description": """  Prevent confirmation of sale orders when margin is below a minimum threshold.
                        Managers can bypass the restriction.
                        """,
    "author": "Farid SLIMANI",
    "license": "LGPL-3",
    'price': 29,
    'support': 'imazighenapps@gmail.com',
    'currency': 'EUR',

    "depends": ["sale", "product"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/sale_order_view.xml",
        "views/res_config_settings_view.xml",
    ],
    "installable": True,
    "application": False,
}
