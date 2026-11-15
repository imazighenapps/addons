# -*- coding: utf-8 -*-
{
    'name': 'PhoneAssign',
    'version': '19.0.1.0.0',
    'summary': 'Track company phones and SIM cards, assign them to employees with issue and return dates, record status changes, and keep a company-safe assignment history.',
    'description': '''PhoneAssign - Company Phone and SIM Assignment
=============================================
Company phones and SIM cards tracked in spreadsheets are easy to lose track of,
especially during onboarding and offboarding. IT needs to know who holds each
device or number and its status.

PhoneAssign provides a catalogue of phones/SIMs and assignment records. Issue an
item to an employee, record its return or mark it lost so the current holder and
history remain visible.

* Phone/SIM items with identifier, number and type.
* Assignments per employee with issue and return dates.
* States: assigned, returned, lost.
* Search and reporting by employee, item and state.
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
        'views/phone_assignment_0_views.xml',
        'views/phone_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
