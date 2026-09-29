{
    'name': 'QMS Context & Compliance',
    'summary': 'Organizational context, interested parties, compliance obligations and opportunities',
    'description': '''


QMS Context & Compliance - Issues to Obligations
===================================================
Analyse organisational context, interested parties and compliance
obligations (ISO 9001 clauses 4, 6.1) and turn them into actions.

Features
--------
* Context issues, interested parties and their needs
* Compliance obligations register with evaluation
* SWOT-style analysis feeding risks and opportunities
* Automatic numbering sequences
    
    
    ''',
    'version': '2.0.1.1.0',
    'category': 'Quality',
    'author': 'FARID SLIMANI',
    'license': 'OPL-1',
    'price': 19,
    'currency': 'EUR',
    'depends': [
        'qms_core',
        'mail',
    ],
    'data': [
        'security/qms_security_groups.xml',
        'data/qms_context_sequence.xml',
        'views/qms_context_views.xml',
        'views/qms_context_menus.xml',
        'security/ir.access.csv',
    ],
    'demo': [
        'demo/qms_demo_context.xml',
    ],
    'images': [
        
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
}
