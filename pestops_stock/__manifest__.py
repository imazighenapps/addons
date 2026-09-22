{
    'name': 'PestOps Stock & Traceability',
    'version': '19.0.1.1.1',
    'category': 'Services',
    'summary': 'Advanced stock traceability and product consumption for PestOps',
    'description': '''
PestOps Stock & Traceability extends PestOps Community with:
- immutable consumption trace records linked to treatments and stock moves;
- lot traceability and lot/expiry controls;
- live availability indicators on treatment consumption lines;
- configurable minimum-stock thresholds by product and internal location;
- automatic low-stock activity alerts;
- operational stock traceability views and pivots.

Designed for Odoo Community 19.0.
''',
    'author': 'Farid SLIMANI',
    'license': 'LGPL-3',
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'pestops_core',
        'stock',
    ],
    'images': ['static/description/banner.png'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/cron.xml',
        'views/pest_stock_trace_views.xml',
        'views/pest_stock_threshold_views.xml',
        'views/pest_stock_menus.xml',
        'views/pest_treatment_stock_views.xml',
    ],
    'application': False,
    'installable': True,
}
