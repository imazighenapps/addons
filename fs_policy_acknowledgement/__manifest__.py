# -*- coding: utf-8 -*-
{
    'name': 'PolicyAck',
    'version': '18.0.1.0.0',
    'summary': 'Maintain a register of company policies and track employee acknowledgements with status and date, providing an auditable per-policy, per-employee trail.',
    'description': '''PolicyAck - Employee Policy Acknowledgement Tracking
====================================================
Policies shared by email or paper are hard to track: HR cannot prove who read and
acknowledged which version. Audits and compliance checks become time-consuming.

PolicyAck provides a policy register and acknowledgement records. Define policies
with version and effective date, assign employees and record acknowledgements so
pending and completed confirmations are visible.

* Policy register with title, version and effective date.
* Acknowledgement records per employee and policy.
* States: pending, acknowledged with acknowledgement date.
* Search and reporting by policy, employee and status.
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
        'views/policy_acknowledgement_0_views.xml',
        'views/hr_policy_1_views.xml',
        'views/menus.xml',
    ],
    'demo': [
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
