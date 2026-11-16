# -*- coding: utf-8 -*-
{
    'name': 'PermitToWorkLog',
    'version': '19.0.1.0.0',
    'summary': 'Authorize and track high-risk work permits with type, location, contractor, validity and states.',
    'description': '''PermitToWorkLog - Permit to Work Register
=========================================
Permits tracked on paper forms make approvals and validity hard to prove.

PermitToWorkLog provides a simple permit register.

* Permits with type, location and work description.
* Contractor or requester and safety measures.
* Validity start and end dates.
* Draft, requested, approved, active, closed and cancelled states.
* Search and grouping by type, location and state.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Project',
    'license': 'OPL-1',
    'price': 39.0,
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
        'views/permit_to_work_log_0_views.xml',
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
