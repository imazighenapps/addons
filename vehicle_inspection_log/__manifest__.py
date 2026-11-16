# -*- coding: utf-8 -*-
{
    'name': 'VehicleInspectionLog',
    'version': '18.0.1.0.0',
    'summary': 'Record periodic vehicle inspections with odometer, check results, inspector and states.',
    'description': '''VehicleInspectionLog - Vehicle Inspection Register
==================================================
Vehicle inspections kept in paper folders hide open defects and missed due
dates.

VehicleInspectionLog provides a simple inspection register.

* Inspections with vehicle plate, model and date.
* Odometer reading at inspection.
* Brake, tyre, light and body check results.
* Responsible inspector and defect notes.
* Draft, passed, defect and cancelled states.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Services',
    'license': 'OPL-1',
    'price': 29.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'hr',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/vehicle_inspection_log_0_views.xml',
        'views/menus.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
