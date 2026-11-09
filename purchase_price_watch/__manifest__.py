# -*- coding: utf-8 -*-
{
    'name': 'PriceWatch',
    'version': '18.0.1.0.0',
    'summary': 'Keep the last purchase price of every product and supplier, compare each new order line with it, and raise a dated alert as soon as a variation crosses your threshold.',
    'description': '''PriceWatch - Supplier Price Movements
=====================================
Purchasing negotiates a price, then every confirm reshapes it quietly: a
delivery surcharge here, a packaging change there, and three orders later the
catalogue costs eight percent more than the deal. Nobody compares two orders
side by side, except when the annual report is late.

PriceWatch does it at every scan. For a window, each confirmed order line is
compared with the last line of the same product and the same vendor. The
variation in percent is recorded with both prices, the product, the vendor
and the line, and one alert is filed whenever the variation crosses the
threshold of the rule. The first order of a product never alerts, and one
alert per line keeps the register short.

* Dated alert per order line, with prev and new price.
* One vendor product pair compared automatically.
* Threshold rule per company, with its owner on the alert.
* First purchase never alerts, replays never duplicate.
* Variation recorded both in percent and in currency.
* Review or ignore an alert, and reopen it.
* Graph of variations by state and vendor.
* Company isolation, window filters.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Purchase/Purchase',
    'license': 'OPL-1',
    'price': 109.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'purchase',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/price_watch_0_views.xml',
        'views/price_watch_rule_1_views.xml',
        'views/price_scan_wizard_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
