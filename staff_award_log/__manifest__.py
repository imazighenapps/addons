# -*- coding: utf-8 -*-
{
    'name': 'StaffAwardLog',
    'version': '19.0.1.0.0',
    'summary': 'Record employee recognitions and awards with type, date, reason and states to keep a visible appreciation history.',
    'description': '''StaffAwardLog - Employee Recognition and Award Register
=======================================================
Employee recognitions recorded informally are hard to track consistently.

StaffAwardLog provides a simple register of awards and recognition events.

* Award records with employee, type and date.
* Reason/description and awarded by.
* Optional value note.
* Draft, announced and cancelled states.
* Recognition history per employee.
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
        'views/staff_award_log_0_views.xml',
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
