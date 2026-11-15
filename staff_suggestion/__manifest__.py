# -*- coding: utf-8 -*-
{
    'name': 'IdeaBox',
    'version': '19.0.1.0.0',
    'summary': 'Collect employee suggestions with category, description and expected benefit, review them through a decision workflow, and track outcomes in a company-safe register.',
    'description': '''IdeaBox - Employee Suggestion and Improvement Log
=================================================
Improvement ideas shared by email or chat are easily lost and rarely tracked to a
decision. Employees lack feedback and managers lack a prioritized view.

IdeaBox provides a suggestion register. Employees submit ideas with context and
expected benefit, managers review and record decisions, and accepted ideas can be
tracked through to completion.

* Suggestions with submitter, category, title and description.
* Expected benefit and reviewer notes.
* States: draft, submitted, under review, accepted, rejected, done.
* Search and reporting by category, state and period.
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
        'views/staff_suggestion_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
