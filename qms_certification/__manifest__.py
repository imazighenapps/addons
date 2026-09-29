{
    'name': 'QMS Certification',
    'summary': 'Certification lifecycle, certificate validity and surveillance planning',
    'description': '''


QMS Certification - Certificates & Surveillance
===================================================
Track certifications, certificate validity and surveillance audits
to stay permanently ready for the certification body.

Features
--------
* Certification lifecycle and certificate register
* Validity and surveillance planning with reminders
* Nonconformities from external audits linked to CAPA
* Readiness view before each surveillance visit
    
    
    ''',
    'version': '20.0.1.1.0',
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
        'data/qms_certification_sequence.xml',
        'data/qms_certification_cron.xml',
        'views/qms_certification_views.xml',
        'security/qms_security.xml',
        'views/qms_certification_menus.xml',
        'security/ir.access.csv',
    ],
    'demo': [
        'demo/qms_demo_certification.xml',
    ],
    'images': [
        'static/description/icon.png',
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
}
