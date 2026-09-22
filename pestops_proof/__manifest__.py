{
    'name': 'PestOps Proof & Signature',
    'version': '18.0.2.3.1',
    'category': 'Services',
    'summary': 'Structured intervention evidence, acceptance and signed proof',
    'description': '''
PestOps proof layer for structured intervention evidence, customer acceptance,
signatures and signed service proof.
''',
    'author': 'Farid SLIMANI',
    'license': 'LGPL-3',
    'price': 69.0,
    'currency': 'EUR',
    'depends': ['pestops_core', 'pestops_equipment'],
    'images': ['static/description/banner.png'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/proof_views.xml',
        'views/visit_views.xml',
        'views/menu.xml',
        'report/proof_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'pestops_proof/static/src/pestops_proof.css',
        ],
    },
    'installable': True,
    'application': False,
}
