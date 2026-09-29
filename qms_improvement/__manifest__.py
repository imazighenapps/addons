{
    'name': 'QMS Improvement',
    'summary': 'Kaizen, improvement actions, measured benefits and lessons learned',
    'description': '''


QMS Improvement - Kaizen & Lessons Learned
================================================
Collect improvement ideas and Kaizen actions, measure real benefits
and capitalise lessons learned across the organisation.

Features
--------
* Improvement proposals with benefit measurement
* Kaizen actions tracked to completion
* Lessons-learned library searchable by process
* Feeds management review with proven gains
    
    
    ''',
    'version': '2.0.1.1.0',
    'category': 'Quality',
    'author': 'FARID SLIMANI',
    'license': 'OPL-1',
    'price': 29,
    'currency': 'EUR',
    'depends': [
        'qms_core',
        'mail',
    ],
    'data': [
        'security/qms_security_groups.xml',
        'data/qms_improvement_sequence.xml',
        'views/qms_improvement_views.xml',
        'views/qms_improvement_menus.xml',
        'security/ir.access.csv',
    ],
    'demo': [
        'demo/qms_demo_improvement.xml',
    ],
    'images': [
        
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
}
