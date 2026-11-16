# -*- coding: utf-8 -*-
{
    'name': 'GasCylinderLog',
    'version': '19.0.1.0.0',
    'summary': 'Track gas cylinders with reference, gas type, capacity, supplier, test dates and states.',
    'description': '''GasCylinderLog - Gas Cylinder Tracking Register
===============================================
Cylinders tracked on slips are lost with their deposits and test dates.

GasCylinderLog provides a simple cylinder register.

* Cylinders with reference, gas type and capacity.
* Supplier partner and storage location.
* Last and next hydrostatic test dates.
* Draft, in use, empty, returned and cancelled states.
* Search and grouping by gas type, supplier and state.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Inventory',
    'license': 'OPL-1',
    'price': 19.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'contacts',
        'hr',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/gas_cylinder_log_0_views.xml',
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
