{
    'name': 'QMS Suppliers',
    'summary': 'Supplier qualification, evaluations and certificate expiry control',
    'description': '''


QMS Suppliers - Qualification & Monitoring
=============================================
Qualify suppliers, record evaluations and keep certificates under
control with expiry alerts and nonconformity history.

Features
--------
* Supplier qualification workflow and approval states
* Periodic evaluations with scoring
* Certificate and document expiry monitoring
* NCR history per supplier for fact-based decisions
    
    
    ''',
    'version': '2.0.1.1.0',
    'category': 'Quality',
    'author': 'FARID SLIMANI',
    'license': 'OPL-1',
    'price': 39,
    'currency': 'EUR',
    'depends': [
        'qms_core',
        'qms_audit',
        'qms_ncr_capa',
        'mail',
    ],
    'data': [
        'data/qms_supplier_cron.xml',
        'views/qms_supplier_views.xml',
        'views/qms_supplier_menus.xml',
        'security/ir.access.csv',
    ],
    'demo': [
        'demo/qms_demo_supplier.xml',
    ],
    'images': [
        'static/description/icon.png',
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
}
