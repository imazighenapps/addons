# -*- coding: utf-8 -*-
{
    'name': 'PermitTrack',
    'version': '18.0.1.0.0',
    'summary': 'Register employee work permits and authorizations with type, reference and expiry dates, compute validity status, and keep a company-safe compliance record.',
    'description': '''PermitTrack - Employee Work Permit and Authorization Records
============================================================
Work permits and authorizations stored in scattered files are easy to overlook.
Expiries missed can create compliance risks and operational disruption.

PermitTrack provides a structured register per employee. Record permit type,
reference, issuer and validity dates; the module shows whether each permit is
valid, expiring soon or expired so HR can renew on time.

* Permit records with employee, type, reference and issuer.
* Issue and expiry dates with computed status.
* States: valid, expired, cancelled.
* Search and reporting by employee, type and status.
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
        'views/work_permit_record_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
