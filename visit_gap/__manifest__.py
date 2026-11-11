# -*- coding: utf-8 -*-
{
    'name': 'GapWatch',
    'version': '20.0.1.0.0',
    'summary': 'Expose the sites whose contractual visit frequency you have let slip, before the customer notices instead.',
    'description': '''GapWatch - No Site Slips Twice
==============================
Service teams promise a regular visit cadence, but once schedules get
busy the sites that quietly slip past their due date are easy to miss.
Without a clear register, the first signal of a missed commitment often
comes from the customer rather than from your own planning.

GapWatch keeps every covered site in Odoo with its required visit
frequency and the date of the last completed visit. The next due date
and overdue gap are computed for you, so teams can immediately see which
locations are on track and which ones need attention. When a visit is
completed, one action refreshes the schedule and stores a clean log for
follow-up. This makes contractual coverage visible before it becomes a
complaint.

* A register of sites with customer, owner and required visit frequency.
* Last visit and next due dates computed and stored for each site.
* Automatic overdue status and overdue day counters.
* One action to record a completed visit and refresh the schedule.
* Stored counters for total and overdue tracked sites.
* Focused list and kanban views to expose missed commitments first.
* Multi-company isolation for separate service organizations.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Field Service',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/visit_site_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
