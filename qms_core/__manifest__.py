{
    'name': 'QMS Core',
    'summary': 'Quality management foundation for requirements, risks, controls and evidence',
    'description': '''


QMS Core - Quality Management Foundation
=========================================
Foundation of the QMS suite: standards and clauses, requirements,
processes, risks, controls and evidence, all linked together for
full ISO 9001 traceability.

Features
--------
* Standards, clauses and requirements repository
* Process approach with risks, controls and evidence
* Multi-company record rules and automated evidence checks
* Base for every other QMS module
    
    
    ''',
    'version': '20.0.1.1.0',
    'category': 'Quality',
    'author': 'FARID SLIMANI',
    'license': 'OPL-1',
    'price': 59,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/qms_security_groups.xml',
        'data/qms_evidence_cron.xml',
        'data/qms_sequence.xml',
        'data/qms_standard_metadata.xml',
        'views/qms_standard_transition_views.xml',
        'views/qms_standard_views.xml',
        'views/qms_requirement_views.xml',
        'views/qms_process_views.xml',
        'views/qms_risk_views.xml',
        'views/qms_control_views.xml',
        'views/qms_evidence_views.xml',
        'views/qms_menus.xml',
        'security/ir.access.csv',
    ],
    'demo': [
        'demo/qms_demo_core.xml',
    ],
    'images': [
        'static/description/icon.png',
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
}
