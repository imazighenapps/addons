{
    'name': 'QMS Dashboard',
    'summary': 'Executive cockpit, compliance matrix and internal readiness indicators',
    'description': '''


QMS Dashboard - Executive Cockpit
==================================
The executive cockpit of the quality system: compliance matrix,
readiness indicators and key figures consolidated from every module.

Features
--------
* Compliance matrix requirements vs evidence
* Readiness and performance indicators at a glance
* Interactive cockpit with drill-down into source records
* Scheduled computation of dashboard figures
    
    
    ''',
    'version': '20.0.1.1.0',
    'category': 'Quality',
    'author': 'FARID SLIMANI',
    'license': 'OPL-1',
    'price': 49,
    'currency': 'EUR',
    'depends': [
        'qms_core',
        'qms_documents',
        'qms_audit',
        'qms_ncr_capa',
        'qms_training',
        'qms_objectives',
        'qms_management_review',
        'qms_context',
        'qms_complaints',
        'qms_measurement',
        'qms_improvement',
    ],
    'data': [
        'data/qms_dashboard_cron.xml',
        'views/qms_dashboard_views.xml',
        'views/qms_requirement_matrix_views.xml',
        'views/qms_dashboard_client.xml',
        'security/qms_security.xml',
        'views/qms_dashboard_menus.xml',
        'security/ir.access.csv',
    ],
    'assets': {'web.assets_backend': ['qms_dashboard/static/src/js/qms_cockpit.js', 'qms_dashboard/static/src/xml/qms_cockpit.xml', 'qms_dashboard/static/src/scss/qms_cockpit.scss']},
    'images': [
        'static/description/icon.png',
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
}
