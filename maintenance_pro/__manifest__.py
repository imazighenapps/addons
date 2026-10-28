# -*- coding: utf-8 -*-
{
    'name': 'MaintenancePro - Equipment Maintenance Management',
    'version': '20.0.1.0.0',
    'summary': 'Keep an equipment register, plan preventive maintenance and track corrective requests with downtime, costs and full history.',
    'description': '''MaintenancePro - Equipment Maintenance Management
=================================================
Your machines break down at the worst moment, and nobody knows what was done
last time, by whom, or how much it cost.

MaintenancePro gives maintenance teams a single register for every machine,
vehicle, tool and IT asset, with its location, serial number, supplier,
warranty and criticality. Preventive plans carry a period in days: the next
due date is computed automatically and a daily scheduler creates the work
order when it is time, without ever duplicating a job. Corrective requests
come from the shop floor, follow a controlled workflow from draft to done, and
record the technician, the scheduled date, the real duration and the cost.
Every intervention updates the equipment history: open requests, last
intervention date and total maintenance cost.

* Equipment register with code, category, location, serial number and
  criticality.
* Warranty tracking, with a control on the warranty end date.
* Preventive plans with a period in days and an automatic next due date.
* Daily scheduler that creates the preventive work orders for you.
* Corrective requests with priority, technician, scheduled date and duration.
* Downtime, duration and cost per intervention, aggregated per equipment.
* Status workflow with chatter, tracking and a full audit trail.
* Search filters and grouped views per equipment, type, state and technician.
* Multi-company equipment register and requests.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Manufacturing/Manufacturing',
    'license': 'OPL-1',
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/maint_equipment_0_views.xml',
        'views/maint_plan_1_views.xml',
        'views/maint_request_2_views.xml',
        'views/menus.xml',
        'data/cron.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
