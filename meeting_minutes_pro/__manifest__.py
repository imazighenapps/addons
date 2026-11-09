# -*- coding: utf-8 -*-
{
    'name': 'MinuteBook',
    'version': '18.0.1.0.0',
    'summary': 'Write structured meeting minutes with attendees, agenda, decisions and assigned action items, then follow every action until it is done or overdue.',
    'description': '''MinuteBook - Minutes and Action Items
=====================================
A meeting ends, everybody leaves with three decisions and a list of tasks
in their head. Two weeks later nobody remembers who agreed to send the
contract, and the only trace of the meeting is a shared document nobody
opens again.

MinuteBook writes the minutes while they are still fresh. Each meeting
carries its date, place, chair, attendees and agenda, then the decisions
that were taken. Action items are separate records with an owner, a due
date and a status: to do, done or cancelled. They are listed inside the
meeting and in their own menu, so the same list becomes the agenda of the
next meeting. An action whose due date has passed is flagged as overdue,
the meeting counts its actions and its open actions, and closing the
minutes is refused as long as no decision has been recorded. Every state
change is written in the chatter, and each company only sees its own
meetings.

* Minutes with date, place, chair and attendees.
* Agenda and decisions in dedicated fields.
* Action items with an owner, a due date and a status.
* Overdue flag computed from the due date and the status.
* Action and open action counters on every meeting.
* Draft, held, closed and cancelled states with an audit trail.
* Closing refused while the decisions are still empty.
* Kanban by state, multi-company isolation, no external dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Productivity/Productivity',
    'license': 'OPL-1',
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/meeting_minute_0_views.xml',
        'views/meeting_action_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
