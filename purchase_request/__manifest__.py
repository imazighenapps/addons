# -*- coding: utf-8 -*-
{
    'name': 'PurchaseRequest',
    'version': '20.0.1.0.0',
    'summary': 'Capture internal purchase requests with requester, needed date and lines, run a submit/approve workflow, and track requisitions through to ordered status in a company-safe register.',
    'description': '''PurchaseRequest - Internal Purchase Requests
===============================================
Employees request goods and services by email or chat, leaving buyers with
incomplete information and no approval trail. Purchase orders get created
without a clear record of the original need.

PurchaseRequest introduces an internal requisition step before ordering. A
requester submits a requisition with lines describing what is needed and when;
a manager approves it and the buyer marks it as ordered once the purchase is
placed. The team keeps a traceable path from need to order.

* Requisitions with requester, department, needed date and priority.
* Lines with product/description, quantity and estimated unit price.
* Workflow: draft, submitted, approved, ordered, done, cancelled.
* Approval gate before a requisition can be marked ordered.
* Search and reporting by requester, state and period.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Purchase',
    'license': 'OPL-1',
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'purchase',
        'hr',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/purchase_request_0_views.xml',
        'views/purchase_request_line_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
