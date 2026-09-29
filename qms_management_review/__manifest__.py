{
    'name': 'QMS Management Review',
    'summary': 'Management-review preparation, decisions and accountable actions',
    'description': '''


QMS Management Review - Decisions & Actions
================================================
Prepare management reviews with consolidated inputs, record decisions
and assign accountable actions with deadlines.

Features
--------
* Review preparation aggregating audits, NCRs, objectives and KPIs
* Decisions, accountable actions and due dates
* Follow-up of previous review actions
* Full history for certification audits
    
    
    ''',
    'version': '2.0.1.1.0',
    'category': 'Quality',
    'author': 'FARID SLIMANI',
    'license': 'OPL-1',
    'price': 29,
    'currency': 'EUR',
    'depends': [
        'qms_core',
        'qms_audit',
        'qms_ncr_capa',
        'qms_training',
        'qms_objectives',
        'qms_supplier',
        'qms_measurement',
        'qms_context',
        'qms_complaints',
        'qms_improvement',
        'mail',
    ],
    'data': [
        'data/qms_review_sequence.xml',
        'views/qms_review_views.xml',
        'views/qms_review_menus.xml',
        'security/ir.access.csv',
    ],
    'demo': [
        'demo/qms_demo_review.xml',
    ],
    'images': [
        
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
}
