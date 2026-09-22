{
    'name': 'PestOps Suite',
    'version': '19.0.3.0.1',
    'category': 'Services',
    'summary': 'Pest control vertical ERP suite for Odoo 19 Community',
    'description': '''
Meta-module for installing the complete PestOps Community suite.
It contains no business logic; it aggregates the feature modules.
''',
    'author': 'PestOps',
    'license': 'LGPL-3',
    'price': 0.0,
    'currency': 'EUR',
    'depends': ['pestops_core', 'pestops_sale', 'pestops_account', 'pestops_stock', 'pestops_portal', 'pestops_calendar', 'pestops_automation', 'pestops_equipment', 'pestops_quality', 'pestops_analytics', 'pestops_proof', 'pestops_localization', 'pestops_hardening'],
    'images': ['static/description/banner.png'],
    'data': [],
    'installable': True,
    'application': True,
}
