{
    'name': 'PestOps Accounting',
    'version': '19.0.1.2.1',
    'category': 'Services/Accounting',
    'summary': 'PestOps contract billing and invoice generation for Odoo Community',
    'description': '''
PestOps Accounting adds the financial layer for pest control contracts:
billing periods, per-visit billing items, additional billable services,
invoice generation and contract billing KPIs.

It uses Odoo Community Invoicing/Accounting rather than recreating accounting logic.
''',
    'author': 'Farid SLIMANI',
    'license': 'LGPL-3',
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'pestops_core',
        'account',
    ],
    'images': ['static/description/banner.png'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/pest_billing_item_views.xml',
        'views/pest_contract_views.xml',
        'views/pest_account_menus.xml',
    ],
    'application': False,
    'installable': True,
}
