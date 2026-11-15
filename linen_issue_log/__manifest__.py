# -*- coding: utf-8 -*-
{
    'name': 'LinenIssueLog',
    'version': '18.0.1.0.0',
    'summary': 'Track linen issues and returns with item, quantity, recipient, dates and states to control circulation and outstanding items.',
    'description': '''LinenIssueLog - Linen Issue and Return Register
===============================================
Linen movements tracked on paper make it hard to know what is outstanding,
returned or lost.

LinenIssueLog records each issue and return with quantity, recipient and
status.

* Issue/return records with item description and quantity.
* Recipient, responsible user and issue/return dates.
* Condition and notes for losses or damage.
* Draft, issued, returned and cancelled states.
* Visibility on outstanding items.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Project',
    'license': 'OPL-1',
    'price': 19.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'hr',
        'contacts',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/linen_issue_log_0_views.xml',
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
