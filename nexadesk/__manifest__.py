# -*- coding: utf-8 -*-
{
    'name': 'Nexadesk',
    'version': '18.0.1.0.0',
    'category': 'Hidden',
    'summary': 'Custom home launcher for Odoo',
    'author': 'Farid SLIMANI',
    'website': 'imazighenapps@gmail.com',
    'license': 'LGPL-3',
    'price': 27.00,
    'currency': 'EUR',
    'depends': ['web'],
    'assets': {
        'web.assets_backend': [
            'nexadesk/static/src/css/launcher.css',
            'nexadesk/static/src/xml/launcher.xml',
            'nexadesk/static/src/js/launcher.js',
        ],
    },

    'images': ['static/description/img.gif'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
