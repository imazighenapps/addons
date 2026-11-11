# -*- coding: utf-8 -*-
{
    'name': 'ReturnDesk',
    'version': '18.0.1.0.0',
    'summary': 'Run customer returns properly: request, approval, inbound receipt, keep or scrap, and the credit the customer awaits.',
    'description': '''ReturnDesk - Returns Handled Like Sales
=======================================
Customer returns arrive as emails, phone calls and sticky notes: the
request is approved in a hurry, the inbound parcel is received without a
decision, and the credit note the customer expects is forgotten. When a
return is disputed, nobody can show when it was approved or what was done
with the goods.

ReturnDesk gives every return a tracked request in Odoo with the customer,
the reason and the returned lines. Requests move from draft to approved, to
received and finally to resolved with a clear keep-or-scrap decision and a
credit amount. Line quantities must stay positive, an approved request can
be refused, and the resolved totals are computed from the returned goods.
The return the customer asks about is the one the register already traces.

* Return requests with customer, reason and requested date.
* Returned lines with product, quantity and unit value.
* A workflow from draft to approved, received and resolved.
* Approve, refuse, receive and resolve actions with traceability.
* A resolution decision to keep, scrap or credit the goods.
* Returned quantities and totals computed and stored on the request.
* Approving a request without lines is refused for you.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'price': 89.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/rma_request_0_views.xml',
        'views/rma_line_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
