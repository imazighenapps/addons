# -*- coding: utf-8 -*-
{
    'name': 'GateBook',
    'version': '19.0.1.0.0',
    'summary': 'Register every truck entering and leaving the site from the gate, to prove the wait you billed or were billed.',
    'description': '''GateBook - The Gate Tells The Truth
===================================
Trucks queue at the gate, arrive early or late, and leave when the
dock is finally free. The wait is argued later from memory, with no
agreed log of when the vehicle entered, when it left and why it
stayed. Demurrage disputes become phone calls instead of facts.

GateBook keeps a gate register for every truck movement with the
plate, the carrier, the driver and the purpose of the visit. The
guard records the entry time on arrival and the exit time on
departure, and the waiting duration is computed and stored for you.
Open visits show what is still on site, closed visits prove the wait
you billed or were billed, and the gate becomes the source of truth.

* A gate register for every truck with plate, carrier and driver.
* Purpose, dock and reference captured on each visit.
* Entry and exit times stamped with a simple gate workflow.
* Waiting duration computed and stored on every closed visit.
* On-site and closed states with a full chatter trail.
* Open visit counters stored on each gate point.
* Multi-company isolation out of the box.
* A factual log to prove the wait you billed or were billed.''',
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
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/gate_point_0_views.xml',
        'views/gate_entry_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
