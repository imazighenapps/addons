# -*- coding: utf-8 -*-
{
    'name': 'PRDesk',
    'version': '19.0.1.0.0',
    'summary': 'Give every department a proper purchase request desk instead of emails to the buyer, from need to order.',
    'description': '''PRDesk - Requests Beat Emails
=============================
Purchase needs arrive by email, chat and hallway conversations: the
buyer cannot tell which request is urgent, which one is approved or
which one has already become an order. Lines get lost, quantities are
copied twice and nobody can explain later who asked for what and when.

PRDesk gives every department one place to raise a purchase request in
Odoo. Each request records the requester, the needed date and a clear
state from draft to done, with lines for the products, descriptions and
quantities to buy. The buyer works from a single queue instead of an
inbox, submits requests for approval, converts approved needs into an
ordered status and keeps the full history in chatter. The need, the
decision and the follow-up stay on one record.

* A purchase request register with requester and needed date.
* Request lines for the product, description and quantity needed.
* A clear workflow from draft to submitted, approved, ordered and done.
* Totals stored on the request for quick filtering and reporting.
* Buyer and department notes kept on the same request.
* One queue to see every request and its current state.
* Actions refuse edits after ordering and keep decisions traceable.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Purchase/Purchase',
    'license': 'OPL-1',
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/pr_request_0_views.xml',
        'views/pr_request_line_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
