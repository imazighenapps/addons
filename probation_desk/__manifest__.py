# -*- coding: utf-8 -*-
{
    'name': 'Probation',
    'version': '20.0.1.0.0',
    'summary': 'Watch every probation period end date and force the review decision before the deadline turns into habit.',
    'description': '''Probation - Decisions Before Deadlines
======================================
Probation periods end quietly when nobody owns the review date. The
employee keeps working, the manager postpones the conversation, and the
company misses the legal window to confirm, extend or end the trial.
HR discovers the gap only when a decision is suddenly urgent.

Probation records one trial period per employee with a start date, a
planned end date and the review deadline that must trigger a decision.
A stored overdue flag highlights periods whose review date has passed
without a decision, so the list of pending reviews is always current.
Managers can confirm, extend or close the probation with a traced state,
and an extension updates the end date while refusing a date earlier than
the start. Multi-company isolation keeps every company in its own book.

* A probation period per employee with start, end and review dates.
* A stored overdue indicator for reviews past their deadline.
* Decisions to confirm, extend or close the probation with a state.
* Extensions update the end date and refuse invalid dates.
* The review date cannot come before the probation start.
* Search filters to focus on pending and overdue reviews.
* Employee-linked periods for HR follow-up.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Human Resources/Employee',
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
        'views/probation_period_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
