# -*- coding: utf-8 -*-
{
    'name': 'FeedBridge - Google and Meta Product Feeds',
    'version': '20.0.1.0.0',
    'summary': 'Generate validated Google Merchant and Meta product feeds in XML or CSV, with a public URL, error report and automatic refresh.',
    'description': '''FeedBridge - Google and Meta Product Feeds
==========================================
Send a clean product catalogue to Google Shopping and Meta, every day.

FeedBridge reads your Odoo products, checks the mandatory fields (title,
price, identifier, link, image), builds a ready-to-use XML or CSV feed, and
publishes it on a stable public URL. Every problem is listed in a clear error
report, so you fix the product instead of guessing why Google rejects it.

* Google Merchant and Meta catalogue formats.
* XML or CSV output, with the official field names.
* Public URL with a secret token, refreshed by a scheduler.
* Validation report: missing title, price, identifier, image.
* Variants exported as separate items.
* Stock and price always in sync with Odoo.
* Works with Odoo Community and Enterprise.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Website/Website',
    'license': 'OPL-1',
    'price': 99.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'product',
        'stock',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/feed_channel_0_views.xml',
        'views/feed_log_1_views.xml',
        'views/menus.xml',
        'data/cron.xml',
        'data/demo_feed.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
