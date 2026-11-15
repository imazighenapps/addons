# -*- coding: utf-8 -*-
{
    'name': 'FuelRequestLog',
    'version': '19.0.1.0.0',
    'summary': 'Record vehicle fuel requests with amount, approval and fulfillment states to control and track fuel usage.',
    'description': '''FuelRequestLog - Fuel Request and Approval Register
===================================================
Fuel requests handled informally lack consistent approvals and traceability.

FuelRequestLog provides a simple request and approval register per vehicle.

* Requests with vehicle, requester and date.
* Requested amount/quantity and purpose notes.
* Approver and fulfillment tracking.
* Draft, submitted, approved, fulfilled and rejected states.
* Request history per vehicle.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Project',
    'license': 'OPL-1',
    'price': 29.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'fleet',
        'hr',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/fuel_request_log_0_views.xml',
        'views/menus.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
