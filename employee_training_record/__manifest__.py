# -*- coding: utf-8 -*-
{
    'name': 'TrainRecord',
    'version': '20.0.1.0.0',
    'summary': 'Track employee trainings and certifications with provider, completion and expiry dates, computed validity status, and company-safe reporting by employee, type and period.',
    'description': '''TrainRecord - Employee Training and Certification Tracking
=========================================================
Training certificates scattered across folders and emails make it hard to know
who is qualified and which mandatory certifications are about to expire. Audits
turn into last-minute searches.

TrainRecord keeps a structured register of trainings per employee. Log the
training type, provider, completion date and validity period; the module computes
whether each record is valid, expiring soon or expired so HR can renew on time
and prove compliance.

* Training records per employee with type, provider and completion date.
* Validity/expiry date with computed status (valid, expiring, expired).
* Certificate reference, duration and cost/notes for evidence.
* Configurable training types per company.
* Search and reporting by employee, type, status and period.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Human Resources/Employee',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'hr',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/employee_training_record_0_views.xml',
        'views/employee_training_type_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
