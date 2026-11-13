# -*- coding: utf-8 -*-
{
    'name': 'Google Sheets Sync',
    'version': '20.0.1.0.0',
    'summary': 'Configure spreadsheet exports for Odoo data, schedule or run syncs, and track export runs and status.',
    'description': '''Google Sheets Sync - Push Odoo data to Google Sheets
====================================================
Teams often share operational reports in Google Sheets. Exporting CSVs
manually is slow and error-prone.

Google Sheets Sync lets users define spreadsheet connections and export
jobs targeting Odoo models/fields with filters. Each run records row count,
status and messages, providing a lightweight reporting bridge without
external Python dependencies.

* Connection profile with spreadsheet/document references.
* Export job definitions (model, domain/filter text, fields mapping).
* Sync runs with row count and status.
* Manual run and reset actions.
* Run history and error messages.
* No external Python dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Productivity/Productivity',
    'license': 'OPL-1',
    'price': 79.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/gsheets_connection_0_views.xml',
        'views/gsheets_job_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
