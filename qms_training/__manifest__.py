{
    'name': 'QMS Training',
    'summary': 'Training assignments, qualification evidence and competency tracking',
    'description': '''


QMS Training - Competency & Qualification
===========================================
Assign trainings, collect qualification evidence and monitor
competencies and expiry dates across the organisation.

Features
--------
* Training plans, sessions and attendance
* Qualification evidence linked to documents and audits
* Expiry alerts and re-training cycles
* Competency matrix per employee and job position
    
    
    ''',
    'version': '2.0.1.1.0',
    'category': 'Quality',
    'author': 'FARID SLIMANI',
    'license': 'OPL-1',
    'price': 19,
    'currency': 'EUR',
    'depends': [
        'qms_core',
        'qms_documents',
        'mail',
    ],
    'data': [
        'data/qms_training_sequence.xml',
        'data/qms_training_cron.xml',
        'views/qms_training_views.xml',
        'views/qms_training_menus.xml',
        'security/ir.access.csv',
    ],
    'demo': [
        'demo/qms_demo_training.xml',
    ],
    'images': [
        
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
}
