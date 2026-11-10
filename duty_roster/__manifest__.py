# -*- coding: utf-8 -*-
{
    'name': 'RosterBook',
    'version': '20.0.1.0.0',
    'summary': 'Plan the on-call roster weeks ahead with fair rotations and the compensation each duty earns.',
    'description': '''RosterBook - Fair Rounds, Weeks Ahead
=====================================
On-call duty is easy to assign once and hard to keep fair over time.
Teams rely on spreadsheets to remember whose turn comes next, which
weekend was swapped, and what compensation was promised for each shift.
When the roster slips, coverage becomes a last-minute negotiation and
the history of who carried the load disappears.

RosterBook lets managers plan duty rosters in advance and record each
assignment with its employee, period and compensation. Every roster can
be prepared, published and closed with a simple workflow, while the
planned slots show at a glance who is on duty and how many hours or
units each assignment represents. Stored totals make it easy to compare
coverage across rosters without recalculating by hand.

With a single place for rotations and compensation, teams can publish a
fair schedule weeks ahead and keep a clear record of the duties that
were actually served.

* Duty rosters with planning period and responsible company.
* Planned duty slots per employee with start, end and compensation.
* A workflow to draft, publish and close each roster.
* Stored counters for slots and total compensation per roster.
* Search filters to review draft, published or closed rosters.
* Grouping by state and period for planning overviews.
* Constraints that refuse invalid dates or negative compensation.
* Multi-company isolation with autonomous employee records in tests.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Human Resources/Employee',
    'license': 'OPL-1',
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/duty_roster_0_views.xml',
        'views/duty_slot_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
