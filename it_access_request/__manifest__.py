# -*- coding: utf-8 -*-
{
    'name': 'AccessRequest',
    'version': '18.0.1.0.0',
    'summary': 'Request, approve and track IT access to systems and resources with justification, workflow states and a company-safe audit trail.',
    'description': '''AccessRequest - IT Access and Permission Requests
=================================================
IT access requested by email or chat lacks a consistent approval trail. IT teams
struggle to prove what was requested, approved, granted or revoked.

AccessRequest provides a structured workflow for access requests. Employees
request access to a system or resource with justification; managers or IT approve
or refuse; IT records when access is granted or revoked.

* Requests with requester, system/resource and access type.
* Justification and needed-by date.
* States: draft, submitted, approved, refused, granted, revoked.
* Search and reporting by requester, system and state.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Services',
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
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/it_access_request_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
