# -*- coding: utf-8 -*-
{
    'name': 'ComplaintLog',
    'version': '18.0.1.0.0',
    'summary': 'Log complaints with source, category, severity and description, assign responsibility, track investigation and resolution states in a company-safe register.',
    'description': '''ComplaintLog - Complaint and Grievance Register
===============================================
Complaints received through mixed channels are easy to lose and slow to resolve
when there is no central case register. Accountability and response quality suffer.

ComplaintLog provides a structured register for complaints and grievances. Record
the source, details and severity, assign an owner, and track progress from intake
to resolution and closure.

* Complaint records with source, date, category and description.
* Severity, responsible and resolution fields.
* States: new, in progress, resolved, closed, cancelled.
* Search and reporting by category, severity and state.
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
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/complaint_register_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
