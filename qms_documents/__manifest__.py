{
    'name': 'QMS Documents',
    'summary': 'Controlled documents, revisions, approvals and acknowledgements',
    'description': '''


QMS Documents - Controlled Documentation
==========================================
Manage controlled documents with revisions, approval workflows and
reading acknowledgements, so everyone always works on the valid version.

Features
--------
* Versioned documents with approval states and validity dates
* Acknowledgements tracking per employee
* Automatic numbering sequences
* Integrated with training qualification evidence
    
    
    ''',
    'version': '20.0.1.1.0',
    'category': 'Quality',
    'author': 'FARID SLIMANI',
    'license': 'OPL-1',
    'price': 49,
    'currency': 'EUR',
    'depends': [
        'qms_core',
        'mail',
    ],
    'data': [
        'data/qms_document_sequence.xml',
        'views/qms_document_views.xml',
        'views/qms_document_menus.xml',
        'security/ir.access.csv',
    ],
    'demo': [
        'demo/qms_demo_documents.xml',
    ],
    'images': [
        'static/description/icon.png',
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
}
