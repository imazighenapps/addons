{
    'name': 'QMS Audits',
    'summary': 'Audit programs, audit checks, findings and evidence traceability',
    'description': '''


QMS Audits - Programs, Checks and Findings
============================================
Plan audit programs, run audit checks from reusable templates and
track findings down to their evidence, from preparation to closure.

Features
--------
* Audit programs, plans and reusable check templates
* Findings linked to requirements, risks and evidence
* Follow-up of corrective actions issued from audits
* Demo data to evaluate the full audit cycle
    
    
    ''',
    'version': '20.0.1.1.0',
    'category': 'Quality',
    'author': 'FARID SLIMANI',
    'license': 'OPL-1',
    'price': 49,
    'currency': 'EUR',
    'depends': [
        'qms_core',
        'qms_training',
        'mail',
    ],
    'data': [
        'data/qms_audit_sequence.xml',
        'views/qms_audit_views.xml',
        'views/qms_audit_program_views.xml',
        'views/qms_audit_menus.xml',
        'security/ir.access.csv',
    ],
    'demo': [
        'demo/qms_demo_audit.xml',
    ],
    'images': [
        'static/description/icon.png',
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
}
