# -*- coding: utf-8 -*-
{
    'name': 'ITAssetLog',
    'version': '20.0.1.0.0',
    'summary': 'Register IT assets with tag/serial, assignee, status and key dates to track assignments and lifecycle states.',
    'description': '''ITAssetLog - IT Asset Assignment Register
=========================================
IT assets tracked in spreadsheets quickly drift from reality, making it hard
to know who holds which device and which assets are available or retired.

ITAssetLog provides a simple register for IT asset assignment and status.

* Asset records with tag/serial, type and model details.
* Current assignee, location and status.
* Purchase/warranty dates and notes.
* Draft, in use, in repair, spare and retired states.
* Assignment and lifecycle notes.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Project',
    'license': 'OPL-1',
    'price': 29.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'hr',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/it_asset_log_0_views.xml',
        'views/menus.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
