# -*- coding: utf-8 -*-
{
    'name': 'WorkOrderLog',
    'version': '20.0.1.0.0',
    'summary': 'Record maintenance interventions with equipment, technician, dates, duration, work done and outcome states to keep a clear repair history.',
    'description': '''WorkOrderLog - Maintenance Work Order Records
=============================================
Maintenance requests describe what needs fixing, but the actual work performed,
time spent and outcome are often buried in comments.

WorkOrderLog adds a structured work order record per intervention, linked to
equipment and optionally to a maintenance request.

* Work orders linked to equipment and maintenance request.
* Technician, planned/start/end dates and duration.
* Work description, parts notes and outcome.
* Draft, in progress, done and cancelled states.
* Intervention history per equipment.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Manufacturing/Maintenance',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'maintenance',
        'hr',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/maintenance_work_order_log_0_views.xml',
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
