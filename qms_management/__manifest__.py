{
    'name': 'QMS Management System',
    'summary': 'End-to-end quality management, audits, CAPA, documents and readiness',
    'description': '''


QMS Management System - Complete Suite
========================================
The complete Quality Management System in one application: documents,
audits, NCR & CAPA, training, objectives, reviews, suppliers and the
executive dashboard, pre-wired and ready for ISO 9001 certification.

Features
--------
* Installs and connects the whole QMS suite at once
* End-to-end traceability from requirement to evidence
* Consolidated menus, reports and readiness indicators
* The fastest path to a certifiable quality system
    
    
    ''',
    'version': '2.0.1.1.0',
    'category': 'Quality',
    'author': 'FARID SLIMANI',
    'license': 'OPL-1',
    'price': 29,
    'currency': 'EUR',
    'depends': [
        'web',
        'qms_core',
        'qms_documents',
        'qms_audit',
        'qms_ncr_capa',
        'qms_training',
        'qms_objectives',
        'qms_management_review',
        'qms_dashboard',
        'qms_supplier',
        'qms_certification',
        'qms_context',
        'qms_complaints',
        'qms_measurement',
        'qms_improvement',
    ],
    'data': [
        'views/qms_management_views.xml',
        'views/qms_reports.xml',
        'views/qms_report_buttons.xml',
    ],
    'images': [
        
        'static/description/banner.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'website': '',
}
