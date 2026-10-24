# -*- coding: utf-8 -*-
{
    'name': 'BackInStock Pro - Back in Stock Alerts',
    'version': '19.0.1.0.0',
    'summary': 'Capture out-of-stock demand, send automatic back-in-stock emails, and measure how much revenue you recover.',
    'description': '''BackInStock Pro - Back in Stock Alerts
======================================
A customer who finds a product out of stock usually leaves and never comes
back. BackInStock Pro captures that demand and turns it into revenue.

Visitors leave their email on the product page. When the product is
replenished, Odoo sends the alert automatically, with a double opt-in and a
clean unsubscribe link. The back-office shows the waiting list, the demand
per product and the conversion.

* "Notify me" capture through a public JSON endpoint.
* Double opt-in confirmation before any marketing email.
* Automatic alert when stock becomes available.
* Waiting list per product and per variant.
* Demand analytics: how many customers wait, for how long.
* One-click unsubscribe and GDPR-friendly consent date.
* Export the waiting list to CSV.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Website/Website',
    'license': 'OPL-1',
    'price': 29.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'stock',
        'product',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/stock_alert_request_0_views.xml',
        'views/menus.xml',
        'data/mail_template.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
