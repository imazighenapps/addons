{
    'name': 'PestOps Quality & Compliance',
    'version': '19.0.1.5.1',
    'category': 'Services',
    'summary': 'Quality procedures, checklists, non-conformities and corrective actions for PestOps',
    'description': '''
PestOps Quality & Compliance adds structured quality and compliance workflows:
procedures, versioned checklists, field quality checks, non-conformities,
corrective/preventive actions and evidence records.

Designed for Odoo Community 19.0.
''',
    'author': 'Farid SLIMANI',
    'license': 'LGPL-3',
    'price': 79.0,
    'currency': 'EUR',
    'depends': [
        'pestops_core',
        'mail',
    ],
    'images': ['static/description/banner.png'],
    'data': [
        'security/pestops_quality_groups.xml',
        'security/ir.model.access.csv',
        'security/pestops_quality_rules.xml',
        'data/sequence.xml',
        'data/cron.xml',
        'views/pest_quality_procedure_views.xml',
        'views/pest_quality_checklist_views.xml',
        'views/pest_quality_check_views.xml',
        'views/pest_quality_nonconformity_views.xml',
        'views/pest_quality_action_views.xml',
        'views/pest_quality_menus.xml',
        'views/pest_visit_views.xml',
        'report/pest_quality_report.xml',
    ],
    'application': False,
    'installable': True,
}
