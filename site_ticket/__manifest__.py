# -*- coding: utf-8 -*-
{
    'name': 'SiteTicket',
    'version': '18.0.1.0.0',
    'summary': 'Turn every building problem into a ticket routed to the right contractor with a deadline and the photos.',
    'description': '''SiteTicket - Buildings Fixed, Not Begged
========================================
A leaking roof is mentioned in the corridor, a broken light is emailed
to nobody in particular and the contractor is called when someone is
already angry. Deadlines are vague, photos live in phones and nobody
can tell what is open, what is late and what it cost.

SiteTicket turns every building problem into a tracked ticket with a
location, a priority, a requested fix date and the contractor in
charge. Each ticket moves from new to in progress, then to done or
cancelled, with the start and resolution dates stamped for you. The
photo note and the cost stay on the record, the open queue is one
screen, and the facilities team stops begging for updates.

* A ticket register for every building issue with location and priority.
* Assignment to an internal owner and to the contractor partner.
* Requested, started and resolved dates stamped on the workflow.
* New, in progress, done and cancelled states with chatter history.
* Cost tracking and a photo or evidence note on each ticket.
* Open and overdue ticket counters kept up to date by location view.
* Multi-company isolation out of the box.
* A clean queue for the issues that still need action.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/site_area_0_views.xml',
        'views/site_ticket_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
