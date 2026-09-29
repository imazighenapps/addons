{
    'name': 'QMS Objectives',
    'summary': 'Measurable quality objectives and performance tracking',
    'description': '''


QMS Objectives - Measurable Quality Goals
============================================
Define measurable quality objectives, track indicators and prove
continual improvement with performance history.

Features
--------
* SMART objectives with target values and deadlines
* Indicator follow-up and performance history
* Objective reviews linked to management review
* Automatic numbering sequences
    
    
    ''',
    'version': '20.0.1.1.0',
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
        'data/qms_objective_sequence.xml',
        'views/qms_objective_views.xml',
        'views/qms_objective_menus.xml',
        'security/ir.access.csv',
    ],
    'demo': [
        'demo/qms_demo_objectives.xml',
    ],
    'images': [
        'static/description/icon.png',
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
}
