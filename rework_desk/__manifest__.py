# -*- coding: utf-8 -*-
{
    'name': 'Rework',
    'version': '18.0.1.0.0',
    'summary': 'Turn rejected production output into a controlled rework order with the trace instead of a whispered fix.',
    'description': '''Rework - Second Pass, Documented
================================
Rejected output is often fixed on the side: a quiet second pass, no
record of what failed, and no proof that the reworked quantity matches
what was rejected. When the customer asks for traceability, the answer
is a memory instead of a file.

Rework turns every rejected lot into a documented case and links it to
a controlled rework order. The rejection captures the product, the
quantity, the reason and the detection date, while the rework order
states what will be done, by whom and when. Quantities are tracked so
the second pass cannot silently exceed what was rejected, and the
order closes only when the rework is completed and recorded.

* A register of rejected production output with quantity and reason.
* Controlled rework orders linked to each rejection.
* A workflow from draft to planned, running and done.
* Quantities compared so rework cannot exceed the rejection.
* Owners and planned dates kept on every rework order.
* Stored counters for rework orders per rejection.
* Completion dates recorded on done orders.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
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
        'views/rwk_reject_0_views.xml',
        'views/rwk_order_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
