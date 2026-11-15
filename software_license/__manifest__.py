# -*- coding: utf-8 -*-
{
    'name': 'LicenseTrack',
    'version': '18.0.1.0.0',
    'summary': 'Register software licenses with vendor, seats and expiry dates, track active/expired/cancelled status, and keep a company-safe license inventory.',
    'description': '''LicenseTrack - Software License and Subscription Register
=========================================================
Software licenses and subscriptions tracked in spreadsheets are easy to overlook.
Missed renewals cause service lapses, while unused seats waste budget.

LicenseTrack provides a structured license register. Record software, vendor,
seats, owner and key dates so IT can monitor renewals and maintain a clear
inventory.

* License records with software, vendor, seats and reference.
* Owner, purchase and expiry dates.
* States: active, expired, cancelled with expiry visibility.
* Search and reporting by vendor, owner and state.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Services',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/software_license_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
