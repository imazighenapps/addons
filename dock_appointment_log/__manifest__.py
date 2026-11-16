# -*- coding: utf-8 -*-
{
    'name': 'DockAppointmentLog',
    'version': '18.0.1.0.0',
    'summary': 'Schedule and track carrier arrivals at loading docks with direction, reference and pallet count.',
    'description': '''DockAppointmentLog - Loading Dock Appointment Register
======================================================
Dock slots booked by phone and whiteboard lead to double bookings and waiting
trucks.

DockAppointmentLog provides a simple dock appointment register.

* Appointments with date/time, dock and inbound/outbound direction.
* Carrier, vehicle plate and shipment reference.
* Pallet count and responsible user.
* Draft, confirmed, done and cancelled states.
* Search and grouping by dock, direction and state.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Inventory',
    'license': 'OPL-1',
    'price': 29.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/dock_appointment_log_0_views.xml',
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
