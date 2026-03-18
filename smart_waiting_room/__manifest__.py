# -*- coding: utf-8 -*-
{
    'name': 'Smart Waiting Room',
    'version': '19.0.1.0.0',
    'category': 'Services/Waiting Room',
    'summary': 'Intelligent queue & waiting room management for clinics, offices, and service centers',
    'description': """
Smart Waiting Room — Intelligent Queue Management
==================================================

A professional, universal waiting room and queue management solution
designed for clinics, dental offices, medical centers, banks,
administration offices, training centers, and any service-based business.

Key Features:
-------------
* Real-time dynamic waiting list with live status updates
* Stunning TV Display Screen (public, no login required)
* Smart prioritization (urgent, VIP, appointment, walk-in)
* Multi-room / Multi-department support
* Estimated wait time calculation
* Internal staff notifications
* Complete visit history & analytics dashboard
* Audio call announcements (browser TTS)
* self-check-in (kiosk mode)
* Multi-language: English, French, Arabic, Spanish, German, Portuguese, Chinese

Compatible with Odoo 19 Community & Enterprise.
    """,
    'author': 'Farid SLIMANI',
    'website': 'imazighenapps@gmail.com',
    'license': 'OPL-1',
    'depends': [
        'base',
        'web',
        'mail',
        'calendar',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sequence_data.xml',
        'data/waiting_room_data.xml',
        'views/waiting_room_views.xml',
        'views/queue_line_views.xml',
        'views/department_views.xml',
        'views/display_screen_template.xml',
        'views/menu_views.xml',
        'report/queue_report.xml',
        'report/queue_report_template.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'smart_waiting_room/static/src/css/waiting_room.css',
            'smart_waiting_room/static/src/js/waiting_room_widget.js',
            'smart_waiting_room/static/src/js/dashboard.js',
        ],
    },
    'images': ['static/description/img.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 99.00,
    'currency': 'EUR',
    
}
