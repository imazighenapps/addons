# -*- coding: utf-8 -*-
{
    'name': 'UniformTrack',
    'version': '18.0.1.0.0',
    'summary': 'Track uniform and PPE items allocated to employees with quantity, issue date and status, record returns or replacements, and keep a company-safe allocation history.',
    'description': '''UniformTrack - Employee Uniform and PPE Allocation
==================================================
Uniforms and PPE issued to employees are often tracked in spreadsheets, making it
hard to know what each person holds and what needs replacement.

UniformTrack provides an item catalogue and allocation records. Issue items to
employees with quantity and dates, update status when items are returned or
replaced, and keep a clear history per employee.

* Uniform/PPE items with name and type.
* Allocations per employee with quantity, issue date and size/notes.
* States: issued, returned, replaced.
* Search and reporting by employee, item and state.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Human Resources/Employee',
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
        'views/uniform_allocation_0_views.xml',
        'views/uniform_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
