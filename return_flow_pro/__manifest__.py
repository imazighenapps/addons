# -*- coding: utf-8 -*-
{
    'name': 'ReturnFlow Pro',
    'version': '19.0.1.0.0',
    'summary': 'Handle customer returns from validated deliveries: multi-line returns with configurable motives, a received/inspected workflow with restock, repair or scrap outcome, and a guided credit note in one company-safe desk.',
    'description': '''ReturnFlow Pro - Customer Returns Desk
======================================
A customer return handled by a raw reverse transfer leaves no trail: no
motive, no eligibility check, no decided physical outcome and no direct
link to the credit note. The warehouse improvises, quality loses the
signal, and accounting rebuilds the refund by hand.

ReturnFlow Pro turns every return into a traced object. Create a return
from a validated delivery, pick the lines and quantities to send back and
choose a configurable return motive. The workflow makes the state explicit:
requested, received, inspected, then closed on a single outcome - restock,
repair or scrap. Restocking posts the incoming move, scrapping does not.
Once inspected, a credit note is generated in one click, pre-filled with
the validated return lines, so the refund stays tied to the return.

* Create a multi-line return from a validated delivery.
* Configurable return motives and a per-motive view of returns.
* Workflow: requested, received, inspected, restocked / repaired / scrapped.
* Returned quantity can never exceed the delivered quantity.
* Restock posts stock back in; scrap keeps it out of stock.
* Guided credit note pre-filled from the inspected return.
* Kanban and search by customer, product, motive and state.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Inventory',
    'license': 'OPL-1',
    'price': 79.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'stock',
        'sale',
        'account',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/return_request_0_views.xml',
        'views/return_line_1_views.xml',
        'views/return_reason_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
