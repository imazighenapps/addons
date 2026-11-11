# -*- coding: utf-8 -*-
{
    'name': 'VisitPlan',
    'version': '20.0.1.0.0',
    'summary': 'Plan each week of site visits per technician with the sensible travel order instead of the phone ping-pong.',
    'description': '''VisitPlan - Routes That Respect The Map
=======================================
Technicians often learn their weekly route through scattered calls and
messages, which leads to wasted travel time and missed appointments. When
several sites must be covered in the same area, the order of visits is
decided on the fly and nobody keeps a clear record of what was planned.

VisitPlan gives each technician a weekly route in Odoo with an ordered
list of stops. You define the week, assign the owner, and schedule every
visit in the sensible travel sequence before the team leaves. Planned
stops move to done as work is completed, while counters keep the route
status visible without manual tracking. The result is a clear plan that
reduces back-and-forth and makes weekly coverage easy to review.

* Weekly visit plans assigned to a technician and company.
* Ordered stops with customer, site reference and planned date.
* Simple workflow to move a route from draft to planned to done.
* One action to mark each stop as completed on site.
* Stored counters for total, planned and completed stops.
* Search filters and groupings for owners, states and customers.
* Company isolation so each team sees only its own routes.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Field Service',
    'license': 'OPL-1',
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/visit_plan_0_views.xml',
        'views/visit_stop_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
