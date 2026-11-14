# -*- coding: utf-8 -*-
{
    'name': 'SupplyRequest',
    'version': '18.0.1.0.0',
    'summary': 'Capture internal office supply requests with requester, needed date and item lines, run a submit/approve/fulfill workflow, and track requests in a company-safe register.',
    'description': '''SupplyRequest - Internal Office Supply Requests
===============================================
Small office supply needs requested by email or chat are easy to lose and hard
to track. Managers lack visibility on what is requested, approved and fulfilled.

SupplyRequest provides a simple internal request workflow. Employees submit item
lines with quantities and a needed date, a manager approves the request and marks
it fulfilled when delivered.

* Supply requests with requester, needed date and priority.
* Item lines with description and quantity.
* Workflow: draft, submitted, approved, fulfilled, cancelled.
* Approval before fulfillment.
* Search and reporting by requester, state and period.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Services',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'hr',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/office_supply_request_0_views.xml',
        'views/office_supply_request_line_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
