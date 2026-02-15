# -*- coding: utf-8 -*-
{
    'name': 'Meeting Management',
    'version': '18.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Complete Meeting Management System with tracking and reporting',
    'description': """
Meeting Management System
=========================

Features:
* Meeting creation and tracking
* Project and client linkage
* Participant management with roles
* Planned vs actual duration tracking
* Workflow validation system
* Interactive dashboard (Kanban, Graph, Pivot)
* Automatic status updates via cron
* Comprehensive PDF reporting
* Access control with user groups
    """,
    'author': 'Farid SLIMANI',
    'website': 'imazighenapps@gmail.com',
    'license': 'OPL-1',
    'price': 49.00,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'calendar',
        'project',
    ],
    'data': [
        'security/meeting_security.xml',
        'security/ir.model.access.csv',
        'data/meeting_cron.xml',
        'views/meeting_views.xml',
        'views/participant_views.xml',
        'views/dashboard_views.xml',
        'views/meeting_menus.xml',
        'reports/meeting_report.xml',
        'reports/meeting_report_templates.xml',
    ],
    'demo': [],
    'images': ['static/description/img.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
