# -*- coding: utf-8 -*-
{
    'name': 'UniformIssueLog',
    'version': '19.0.1.0.0',
    'summary': 'Record uniform and workwear issues and returns with employee, item details, dates and states.',
    'description': '''UniformIssueLog - Uniform and Workwear Issue Register
=====================================================
Uniform allocations tracked on paper make it hard to know what is issued,
returned or outstanding.

UniformIssueLog provides a simple issue and return register.

* Issue records with employee, item description, size and quantity.
* Issue, expected return and actual return dates.
* Responsible issuer and condition notes.
* Draft, issued, returned and cancelled states.
* Allocation history per employee.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Human Resources/Employees',
    'license': 'OPL-1',
    'price': 19.0,
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
        'views/uniform_issue_log_0_views.xml',
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
