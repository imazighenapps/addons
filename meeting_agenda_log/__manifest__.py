# -*- coding: utf-8 -*-
{
    'name': 'MeetingAgenda',
    'version': '18.0.1.0.0',
    'summary': 'Plan meetings with agendas and attendees, record outcomes and action items, and track follow-up through clear workflow states.',
    'description': '''MeetingAgenda - Meeting Agenda and Action Log
=============================================
Meetings run without structured agendas lead to unclear objectives and missed
action items. Notes scattered across emails make follow-up hard.

MeetingAgenda provides a structured meeting log. Capture agenda topics, attendees,
outcomes and actions, and track meetings from planning to completion.

* Meeting records with title, date, organizer and attendees.
* Agenda topics, outcomes and action item notes.
* States: draft, planned, done, cancelled.
* Search and reporting by organizer, state and period.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Productivity/Productivity',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/meeting_agenda_log_0_views.xml',
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
