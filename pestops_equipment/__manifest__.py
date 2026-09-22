{
    'name': 'PestOps Equipment',
    'version': '19.0.1.4.1',
    'category': 'Services',
    'summary': 'Equipment, vehicles, PPE and maintenance tracking for PestOps',
    'description': '''
PestOps Equipment adds operational tracking for non-consumable field assets:
equipment, vehicles, PPE, assignments, inspections, maintenance and visit usage.

Designed for Odoo Community 19.0.
''',
    'author': 'Farid SLIMANI',
    'license': 'LGPL-3',
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'pestops_core',
        'mail',
        'stock',
    ],
    'images': ['static/description/banner.png'],
    'data': [
        'security/pestops_equipment_groups.xml',
        'security/ir.model.access.csv',
        'security/pestops_equipment_rules.xml',
        'data/sequence.xml',
        'data/cron.xml',
        'views/pest_equipment_views.xml',
        'views/pest_equipment_assignment_views.xml',
        'views/pest_equipment_inspection_views.xml',
        'views/pest_equipment_maintenance_views.xml',
        'views/pest_equipment_usage_views.xml',
        'views/pest_equipment_menus.xml',
    ],
    'application': False,
    'installable': True,
}
