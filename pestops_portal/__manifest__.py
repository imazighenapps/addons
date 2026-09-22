{
    'name': 'PestOps Portal',
    'version': '18.0.1.0.1',
    'category': 'Services',
    'summary': 'Customer portal for PestOps sites, visits, reports and service requests',
    'description': '''
PestOps Portal extends the Odoo Community customer portal with a dedicated
customer space for pest control contracts operations.

Customers can review their authorized sites and visits, download PestOps
service documents and submit service requests such as re-services or
additional visits.
''',
    'author': 'Farid SLIMANI',
    'license': 'LGPL-3',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'pestops_core',
        'portal',
    ],
    'images': ['static/description/banner.png'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/service_request_views.xml',
        'views/portal_document_views.xml',
        'views/pestops_menus.xml',
        'views/portal_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'pestops_portal/static/src/scss/pestops_portal.scss',
        ],
    },
    'application': False,
    'installable': True,
}
