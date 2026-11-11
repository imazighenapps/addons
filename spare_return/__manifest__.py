# -*- coding: utf-8 -*-
{
    'name': 'SpareBack',
    'version': '18.0.1.0.0',
    'summary': 'Track the spare parts and samples sent to site and get back what the job did not consume.',
    'description': '''SpareBack - What Goes Out Comes Back
====================================
Technicians leave for a job with spare parts and samples, but once the
work is done the unused material often stays in vans or on site. Without
a simple register, nobody knows what was sent, what was consumed and
what should have come back to stock.

SpareBack records every field material movement in Odoo with the
customer, the destination site and the expected return date. Each line
tracks the quantity sent, consumed and returned, so outstanding items
remain visible until they are recovered. When material comes back, one
action closes the line with the returned quantity and date. Teams get a
clear view of what is still due instead of relying on memory.

* Field material lines with customer, site and technician owner.
* Quantities sent, consumed and returned tracked on every line.
* Due dates to highlight material that should come back.
* One action to register the return and close the line.
* Stored counters for open and recovered material lines.
* Search filters for overdue, open and recovered returns.
* Multi-company isolation for separate service operations.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Field Service',
    'license': 'OPL-1',
    'price': 29.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/spare_return_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
