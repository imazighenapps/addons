# -*- coding: utf-8 -*-
{
    'name': 'VisitorParcelLog',
    'version': '18.0.1.0.0',
    'summary': 'Log incoming parcels with recipient, carrier, arrival, storage location and pickup states to track deliveries at reception.',
    'description': '''VisitorParcelLog - Parcel and Delivery Register
===============================================
Incoming parcels tracked on paper are easy to misplace and recipients are not
notified reliably.

VisitorParcelLog provides a simple register of deliveries and pickups.

* Parcel records with recipient, sender/carrier and arrival date.
* Tracking reference and storage location.
* Received and collected details.
* Received, notified, collected and returned states.
* Notes and description.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Project',
    'license': 'OPL-1',
    'price': 19.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'hr',
        'contacts',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/visitor_parcel_log_0_views.xml',
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
