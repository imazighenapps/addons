# -*- coding: utf-8 -*-
{
    'name': 'Toolbox',
    'version': '20.0.1.0.0',
    'summary': 'Log the five-minute safety briefings with whose attended, so the topic and the date stand in your file.',
    'description': '''Toolbox - Five Minutes, Remembered
==================================
Short safety briefings happen on the shop floor: a foreman gathers the
team, covers a topic in five minutes and everyone goes back to work. A
week later, nobody can prove who was there, what was discussed or on
which date, and the safety file is a stack of signatures that never made
it past the clipboard.

Toolbox keeps one Odoo record per toolbox talk: the topic, the date,
the location and the employee who led it. Each attendance line names the
employee who took part and stamps the sign-off when the person confirms
presence, so the attendance count is computed for you. Completed talks
are closed once the briefing is over, and the open-talks screen shows
what still needs to be logged. When the safety file is reviewed, the
topic, the date and the attendees are already on record.

* A register of toolbox talks with topic, date, location and leader.
* Attendance lines with employee and a stamped sign-off.
* Attendance counts computed and stored on every toolbox talk.
* A simple flow from planned to completed for each briefing.
* One open-talks screen for briefings not yet completed.
* A completed talk cannot be completed twice.
* Attendance cannot be added once the talk is completed.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/toolbox_talk_0_views.xml',
        'views/toolbox_attendance_1_views.xml',
        'views/toolbox_open_2_views.xml',
        'views/menus.xml',
        'views/toolbox_open_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
