# -*- coding: utf-8 -*-
{
    'name': 'NearMissLog',
    'version': '19.0.1.0.0',
    'summary': 'Record near misses with location, severity, reporter, corrective action and states.',
    'description': '''NearMissLog - Near Miss Report Register
=======================================
Near misses reported on paper lose the pattern and the follow-up.

NearMissLog provides a simple near miss register.

* Reports with event date, location and description.
* Severity: low, medium, high.
* Reporter and corrective action.
* Draft, reported, investigating, closed and cancelled states.
* Search and grouping by severity, location and state.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Project',
    'license': 'OPL-1',
    'price': 29.0,
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
        'views/near_miss_log_0_views.xml',
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
