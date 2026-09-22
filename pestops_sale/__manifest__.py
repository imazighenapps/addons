{
    'name': 'PestOps Sales Integration',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Connect Odoo Sales with PestOps contracts',
    'description': '''
Optional Community integration between Sales and PestOps Core.
Create a PestOps contract from a quotation/order and automatically activate
the linked contract when the sales order is confirmed.
''',
    'author': 'Farid SLIMANI',
    'license': 'LGPL-3',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'pestops_core',
        'sale_management',
    ],
    'images': ['static/description/banner.png'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/pest_contract_views.xml',
    ],
    'application': False,
    'installable': True,
}
