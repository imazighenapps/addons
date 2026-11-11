# -*- coding: utf-8 -*-
{
    'name': 'MedVisit',
    'version': '19.0.1.0.0',
    'summary': 'Track the occupational medical visits of every employee and never discover an overdue one at the worst time.',
    'description': '''MedVisit - Visits Never Overdue
===============================
Occupational medical visits come with legal deadlines that differ by
role, exposure and country, yet the dates are often kept in a shared
calendar or a personal spreadsheet. When an employee changes position or
returns from leave, the next visit date is easy to miss and the first
sign of trouble is an audit asking for proof.

MedVisit records every occupational medical visit per employee with its
type, scheduled date and due date, and computes a stored overdue flag so
the list of visits to chase is always up to date. Completing a visit
stamps the completion date and moves the record out of the overdue
queue, while a cancellation keeps the history without polluting the
agenda. A due date before the scheduled date is refused, and the visit
cannot be closed without a completion date. Multi-company isolation
keeps each company in its own medical book.

* A medical visit per employee with type, schedule and due date.
* A stored overdue indicator computed from the due date.
* Completion and cancellation actions with a traced status.
* The visit cannot be completed without a completion date.
* A due date before the scheduled date is refused for you.
* Search filters to surface overdue and upcoming visits quickly.
* Employee-linked visits for HR follow-up.
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
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/medical_visit_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
