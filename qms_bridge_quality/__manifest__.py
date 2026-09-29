{
    'name': 'QMS Quality Bridge',
    'summary': 'Create NCRs directly from failed Odoo Quality checks',
    'description': '''


QMS Quality Bridge - Failed Checks to NCR
=============================================
Automatically create a nonconformity when an Odoo Quality check
fails, with full context (operation, product, lot) pre-filled.

Features
--------
* One-click or automatic NCR creation from failed checks
* Product, lot and operation carried over to the NCR
* Auto-installed with the Quality app
* Closes the loop between control and corrective action
    
    
    ''',
    'version': '2.0.1.1.0',
    'category': 'Quality',
    'author': 'FARID SLIMANI',
    'license': 'OPL-1',
    'price': 9,
    'currency': 'EUR',
    'depends': [
        'qms_ncr_capa',
        'quality',
    ],
    'data': [
        'security/qms_security.xml',
        'views/bridge_views.xml',
        'security/ir.access.csv',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
