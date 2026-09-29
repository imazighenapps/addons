{
    'name': 'QMS Measurement',
    'summary': 'Measurement equipment, calibration history and metrology control',
    'description': '''


QMS Measurement - Calibration & Metrology
================================================
Keep measurement equipment under control: calibration history,
due dates and out-of-tolerance handling for reliable results.

Features
--------
* Equipment register with characteristics and locations
* Calibration history and next-due-date planning
* Out-of-tolerance alerts and impact assessment
* Links measurement results to evidence
    
    
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
        'data/qms_measurement_data.xml',
        'views/qms_measurement_views.xml',
        'views/qms_measurement_menus.xml',
        'security/ir.access.csv',
    ],
    'demo': [
        'demo/qms_demo_measurement.xml',
    ],
    'images': [
        
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
}
