{
    'name': 'QMS NCR & CAPA',
    'summary': 'Nonconformities, root-cause analysis, corrective actions and effectiveness',
    'description': '''


QMS NCR & CAPA - Nonconformities to Effectiveness
====================================================
Record nonconformities, analyse root causes with structured methods
and drive corrective actions until effectiveness is proven.

Features
--------
* NCR lifecycle with severity, costs of non-quality and containment
* Root-cause analysis (5 Why, Ishikawa) and action plans
* Effectiveness checks before closure
* Bridges create NCRs from Quality, Sales, Stock and MRP
    
    
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
        'mail',
    ],
    'data': [
        'data/qms_ncr_sequence.xml',
        'views/qms_ncr_views.xml',
        'views/qms_quality_cost_views.xml',
        'views/qms_ncr_menus.xml',
        'security/ir.access.csv',
    ],
    'demo': [
        'demo/qms_demo_ncr.xml',
    ],
    'images': [
    
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
}
