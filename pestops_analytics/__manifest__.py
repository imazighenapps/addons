{
    'name': 'PestOps Analytics & Business Intelligence',
    'version': '19.0.2.0.1',
    'category': 'Services/Reporting',
    'summary': 'Management analytics and operational KPIs for PestOps',
    'description': '''
PestOps Analytics turns the operational data already captured by PestOps into
management-ready reports and KPI views.

Includes:
- executive company KPIs;
- visit and technician performance analytics;
- site performance and service quality analytics;
- contract portfolio and billing analytics;
- financial reporting from PestOps billing items;
- stock consumption reporting;
- quality/non-conformity reporting;
- maintenance cost visibility.

Designed for Odoo Community 19.0. Reports are read-only SQL views and use
Odoo Community modules as the source of truth.
''',
    'author': 'Farid SLIMANI',
    'license': 'LGPL-3',
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'pestops_core',
        'pestops_account',
        'pestops_stock',
        'pestops_quality',
        'pestops_equipment',
    ],
    'images': ['static/description/banner.png'],
    'data': [
        'security/ir.model.access.csv',
        'views/pest_analytics_views.xml',
        'views/pest_analytics_menus.xml',
    ],
    'application': False,
    'installable': True,
}
