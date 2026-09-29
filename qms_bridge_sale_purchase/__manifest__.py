{
    'name': 'QMS Sales Purchase Bridge',
    'summary': 'Connect NCRs to Sales and Purchase orders',
    'description': '''


QMS Sales & Purchase Bridge - Orders to NCR
==================================================
Connect nonconformities to sales and purchase orders so customer
claims and supplier issues stay traceable to their documents.

Features
--------
* NCRs linked to sale and purchase order lines
* Complaint-to-order traceability for 8D reports
* Supplier NCRs pre-filled with purchase data
* Auto-installed with Sales and Purchase
    
    
    ''',
    'version': '2.0.1.1.0',
    'category': 'Quality',
    'author': 'FARID SLIMANI',
    'license': 'OPL-1',
    'price': 19,
    'currency': 'EUR',
    'depends': [
        'qms_ncr_capa',
        'sale',
        'purchase',
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
