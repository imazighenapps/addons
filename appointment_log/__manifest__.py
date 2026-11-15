# -*- coding: utf-8 -*-
{
    'name': 'AppointmentLog',
    'version': '20.0.1.0.0',
    'summary': 'Log external appointments with contact, date, subject, outcome and next actions, track planned/done/cancelled states, and report follow-ups in a company-safe register.',
    'description': '''AppointmentLog - External Appointment and Visit Log
==================================================
Appointments tracked only in calendars lose their outcomes and next steps.
Follow-ups are missed when there is no consistent record of what was discussed.

AppointmentLog provides a simple appointment register. Record who you met, when
and why, capture outcomes and next actions, and track status so follow-ups stay
visible.

* Appointments with contact, date, subject and responsible.
* Outcome and next-action fields with follow-up date.
* States: planned, done, cancelled.
* Search and reporting by contact, responsible and period.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/appointment_log_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
