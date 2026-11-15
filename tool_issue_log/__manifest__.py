# -*- coding: utf-8 -*-
{
    'name': 'ToolIssue',
    'version': '18.0.1.0.0',
    'summary': 'Register shared tools and log issues to employees with dates and condition notes, track issued and returned status in a company-safe history.',
    'description': '''ToolIssue - Tool and Equipment Issue Log
========================================
Shared tools handed out informally are hard to track. Items go missing and time
is wasted locating who last used them.

ToolIssue provides a tool catalogue and an issue log. Record which employee took
a tool, when, and its condition, then mark it returned to maintain a clear
accountability trail.

* Tool items with identifier and category.
* Issue records per employee with issue and return dates.
* Condition notes and states: issued, returned.
* Search and reporting by tool, employee and state.
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
        'views/tool_issue_0_views.xml',
        'views/tool_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
