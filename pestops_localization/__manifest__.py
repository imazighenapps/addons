{
    'name': 'PestOps Localization & Internationalization',
    'version': '19.0.2.4.1',
    'category': 'Services',
    'summary': 'Languages, document profiles, country settings and localized PestOps content',
    'description': '''
PestOps localization layer. Uses Odoo native languages, countries and currencies,
while providing company document profiles, localized report content and customer
language preferences for PestOps documents.
''',
    'author': 'PestOps',
    'license': 'LGPL-3',
    'price': 29.0,
    'currency': 'EUR',
    'depends': ['pestops_core'],
    'images': ['static/description/banner.png'],
    'data': [
        'security/ir.model.access.csv',
        'data/document_profile_data.xml',
        'views/localization_views.xml',
        'views/document_profile_views.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'pestops_localization/static/src/pestops_localization.css',
        ],
    },
    'installable': True,
    'application': False,
}
