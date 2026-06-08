# -*- coding: utf-8 -*-
{
    'name': 'Partner Duplicate Detector',
    'version': '18.0.1.0.0',
    'category': 'Contacts',
    'summary': 'Automatically detect and merge duplicate contacts in seconds',
    'description': """
Partner Duplicate Detector
==========================

Instantly detect duplicate contacts in your Odoo database and merge them with one click.

Features:
---------
* Automatic scanning on install — see duplicates in 2 minutes
* Smart similarity scoring (name, email, phone, VAT)
* One-click merge: keeps all history, moves chatter, invoices, sales orders
* Configurable detection threshold
* Scheduled auto-scan (weekly)
* Works on Customers, Vendors and all partner types
* Dashboard with statistics

Perfect for companies that imported data or used Odoo for years.
    """,
    'author': 'Farid SLIMANI',
    'website': 'imazighenapps@gmail.com,
    'license': 'OPL-1',
    'depends': ['contacts', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/duplicate_group_views.xml',
        'views/res_partner_views.xml',
        'views/menu_views.xml',
        'wizard/merge_partner_wizard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'partner_duplicate_detector/static/src/css/duplicate_detector.css',
            'partner_duplicate_detector/static/src/xml/duplicate_detector_templates.xml',
            'partner_duplicate_detector/static/src/js/duplicate_dashboard.js',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 9.00,
    'currency': 'EUR',
}