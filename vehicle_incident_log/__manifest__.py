# -*- coding: utf-8 -*-
{
    'name': 'VehicleIncident',
    'version': '18.0.1.0.0',
    'summary': 'Log company vehicle incidents with vehicle, driver, date and damage details, track follow-up through workflow states, and keep a company-safe incident history.',
    'description': '''VehicleIncident - Company Vehicle Incident Log
==============================================
Vehicle incidents reported informally lead to incomplete records and delayed
follow-up for repairs or insurance. Fleet managers lack consistent vehicle
history.

VehicleIncident provides a structured incident register. Record vehicle, driver,
date, location and damage, track follow-up actions and status until closure.

* Incident records with vehicle, driver, date and location.
* Description, damage and third-party/insurance details.
* States: draft, reported, in progress, closed.
* Search and reporting by vehicle, driver and period.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Human Resources/Fleet',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'fleet',
        'hr',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/vehicle_incident_log_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
