# -*- coding: utf-8 -*-
{
    'name': 'Downtime',
    'version': '18.0.1.0.0',
    'summary': 'Log every machine stop with its reason and compute the availability, MTBF and MTTR the plant really runs at.',
    'description': '''Downtime - Availability, Measured
=================================
Unplanned stops are often discussed from memory, which makes it hard to
know how much time a machine really lost and which reasons repeat most.
Without a consistent log, availability, MTBF and MTTR remain estimates
instead of measurable indicators.

Downtime provides an Odoo register for each machine and every stop event
linked to it. You record the stop reason, start time and end time, and
the module computes the stop duration for each event. Machine counters
then aggregate the number of stops, total downtime and average repair
time so teams can review performance with facts. The result is a simple
timeline that turns scattered interruptions into actionable metrics.

* A machine register with planned operating time for analysis.
* Stop records with reason, start, end and computed duration.
* Running and closed stop states with a one-click close action.
* Stored counters for stop count and total downtime per machine.
* Computed MTTR and availability indicators per machine.
* Search filters and groupings by machine, state and reason.
* Multi-company isolation for separate plants or workshops.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
    'license': 'OPL-1',
    'price': 79.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/downtime_machine_0_views.xml',
        'views/downtime_event_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
