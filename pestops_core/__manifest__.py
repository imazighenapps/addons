{
    'name': 'PestOps Core',
    'version': '19.0.2.3.0',
    'category': 'Services',
    'summary': 'Pest Control Management for Odoo Community',
    'description': '''
PestOps Core adds the operational objects required by pest control companies:
sites, zones, control points, treatment plans, visits, inspections,
treatments, re-services and field anomalies/corrective actions.

Designed for Odoo Community 19.0.
V2.1 adds centralized configuration and productization foundations.
''',
    'author': 'Farid SLIMANI',
    'license': 'LGPL-3',
    'price': 119.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'project',
        'stock',
    ],
    'images': ['static/description/banner.png'],
    'data': [
        'data/technician_action.xml',
        'report/pest_reports.xml',
        'security/pestops_groups.xml',
        'security/ir.model.access.csv',
        'security/pestops_rules.xml',
        'data/sequence.xml',
        'data/default_data.xml',
        'data/cron.xml',
        'views/pest_reference_views.xml',
        'views/pest_contract_views.xml',
        'views/pest_site_views.xml',
        'views/pest_zone_views.xml',
        'views/pest_control_point_views.xml',
        'views/pest_plan_views.xml',
        'views/pest_visit_views.xml',
        'views/pest_inspection_views.xml',
        'views/pest_treatment_views.xml',
        'views/pest_reservice_views.xml',
        'views/pest_anomaly_views.xml',
        'views/pest_menus.xml',
        'views/pest_settings_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
        'demo/demo_v21.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'pestops_core/static/src/technician_app/technician_app.js',
            'pestops_core/static/src/technician_app/technician_app.xml',
            'pestops_core/static/src/technician_app/technician_app.scss',
        ],
    },
    'application': True,
    'installable': True,
}
