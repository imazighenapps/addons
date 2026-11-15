# -*- coding: utf-8 -*-
{
    'name': 'FuelLog',
    'version': '20.0.1.0.0',
    'summary': 'Log vehicle refueling with date, odometer, quantity and cost, keep a vehicle catalogue and track fuel spending per vehicle and period in a company-safe register.',
    'description': '''FuelLog - Vehicle Fuel and Refueling Tracking
=============================================
Fuel receipts and card statements rarely tell the full story per vehicle. Without
a structured refueling log, managers cannot compare consumption, spot anomalies
or explain cost variance.

FuelLog provides a simple vehicle catalogue and a fuel log. Record each refueling
with date, driver, odometer, liters and total cost so spending and usage can be
reviewed per vehicle and period.

* Vehicle catalogue with reference, plate and active flag.
* Fuel log entries with vehicle, driver, date, odometer, liters and cost.
* Computed unit price (cost per liter) for visibility.
* Draft and confirmed states for controlled entries.
* Search and reporting by vehicle, driver and period.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Services',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'hr',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/fuel_log_0_views.xml',
        'views/fuel_vehicle_1_views.xml',
        'views/menus.xml',
    ],
    'demo': [
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
