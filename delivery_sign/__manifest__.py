# -*- coding: utf-8 -*-
{
    'name': 'SignDesk',
    'version': '20.0.1.0.0',
    'summary': 'Capture the signature and photo that prove each delivery reached its customer in the right condition.',
    'description': '''SignDesk - Proof In Every Hand
==============================
When a delivery dispute arises, teams often struggle to prove what was
handed over, when it arrived and in which condition. Without a simple
proof record, customer claims turn into long discussions and missing
evidence.

SignDesk keeps a delivery proof register in Odoo for every outbound
shipment. Each record stores the customer, reference, delivery date and
the evidence collected on site, including the recipient name, signature
confirmation and a photo proof flag. When proof is captured, the
delivery can be marked as signed with a dated trace. Pending and signed
deliveries stay easy to review so service and logistics teams can answer
claims quickly.

* Delivery proof records with customer, reference and delivery date.
* Capture recipient name, signature confirmation and photo proof flag.
* Simple workflow from pending delivery to signed proof.
* Dated action to register signature and delivery evidence.
* Stored counters for pending and signed delivery proofs.
* Search filters to focus on deliveries missing evidence.
* Multi-company isolation for separate logistics teams.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Services',
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
        'views/delivery_proof_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
