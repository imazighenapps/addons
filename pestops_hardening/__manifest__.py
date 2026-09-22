{
    'name': 'PestOps Production Hardening',
    'version': '19.0.2.5.1',
    'category': 'Services',
    'summary': 'Production hardening, operational safeguards and cron idempotency helpers',
    'description': '''
PestOps production hardening layer. Centralizes safe operational settings,
maintenance mode, automation safeguards and integrity checks. Community only.
''',
    'author': 'PestOps',
    'license': 'LGPL-3',
    'price': 19.0,
    'currency': 'EUR',
    'depends': ['pestops_core'],
    'images': ['static/description/banner.png'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/hardening_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': False,
}
