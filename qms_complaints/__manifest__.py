{
    'name': 'QMS Customer Complaints',
    'summary': 'Customer complaint intake, SLA tracking, escalation and portal visibility',
    'description': '''


QMS Customer Complaints - Intake to Resolution
==================================================
Capture customer complaints from the portal or manually, track SLAs,
escalate when needed and convert recurring issues into CAPA.

Features
--------
* Complaint intake with SLA deadlines and escalation
* Customer portal visibility and communication
* Link to NCR & CAPA for systemic issues
* Response-time and recurrence analysis
    
    
    ''',
    'version': '2.0.1.1.0',
    'category': 'Quality',
    'author': 'FARID SLIMANI',
    'license': 'OPL-1',
    'price': 39,
    'currency': 'EUR',
    'depends': [
        'qms_core',
        'qms_ncr_capa',
        'portal',
        'mail',
    ],
    'data': [
        'security/qms_security_groups.xml',
        'data/qms_complaint_data.xml',
        'views/qms_complaint_views.xml',
        'views/qms_complaint_menus.xml',
        'views/qms_complaint_portal.xml',
        'security/ir.access.csv',
    ],
    'demo': [
        'demo/qms_demo_complaints.xml',
    ],
    'images': [
        'static/description/icon.png',
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
}
