# -*- coding: utf-8 -*-
{
    'name': 'TrainBook',
    'version': '20.0.1.0.0',
    'summary': 'Run training sessions from plan to attendance and hand each participant the certificate they can show.',
    'description': '''TrainBook - From Plan To Certificate
====================================
Training plans often live in slides and attendance lives on paper sheets
that never make it back to the office. When a client or an auditor asks
who attended which session and who received a certificate, the answer
requires searching inboxes and folders across several teams. Sessions are
delivered, but the proof is scattered.

TrainBook organizes training sessions in Odoo from the initial plan to
the final certificate. Each session defines the topic, trainer, schedule
and capacity, while attendance lines record every participant and their
status. Managers can confirm a session, mark attendance and issue
certificates in a guided workflow, with stored counters showing how many
participants attended and how many certificates were delivered.

This gives HR and operations a reliable record of what was taught, who
showed up and which certificates can be presented when they are needed.

* Training sessions with topic, trainer, schedule and capacity.
* Attendance lines per employee with presence and certificate status.
* A workflow to plan, confirm, complete and cancel sessions.
* Stored counters for attendees and issued certificates per session.
* Search filters for upcoming, completed and certified sessions.
* Grouping by state and trainer for easy follow-up.
* Constraints on dates, capacity and duplicate participants.
* Multi-company isolation with autonomous employee records in tests.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Human Resources/Employee',
    'license': 'OPL-1',
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/training_session_0_views.xml',
        'views/training_attendance_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
