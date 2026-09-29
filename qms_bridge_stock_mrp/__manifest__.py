{
    'name': 'QMS Stock MRP Bridge',
    'summary': 'Connect NCRs to transfers and manufacturing orders',
    'description': '''


QMS Stock & MRP Bridge - Lots to NCR
===========================================
Attach nonconformities to stock transfers, lots and manufacturing
orders for complete containment and genealogy.

Features
--------
* NCRs linked to pickings, lots and manufacturing orders
* Containment support with lot traceability
* Nonconforming quantity tracked per operation
* Auto-installed with Inventory and MRP
    
    
    ''',
    'version': '2.0.1.1.0',
    'category': 'Quality',
    'author': 'FARID SLIMANI',
    'license': 'OPL-1',
    'price': 19,
    'currency': 'EUR',
    'depends': [
        'qms_ncr_capa',
        'stock',
        'mrp',
    ],
    'data': [
        'security/qms_security.xml',
        'views/bridge_views.xml',
        'security/ir.access.csv',
    ],
    'images': [
        'static/description/icon.png',
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
