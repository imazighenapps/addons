# -*- coding: utf-8 -*-
{
    'name': 'ToolCrib',
    'version': '19.0.1.0.0',
    'summary': 'Lend workshop tools against an employee and a due-back date instead of trusting the open cabinet.',
    'description': '''ToolCrib - Nobody Trusts The Cabinet
====================================
The workshop cabinet is open, drills and torque wrenches disappear for a
day and come back a week later, and nobody can say who took what. A job
stalls because the only calibrated gauge is missing, and the crib master
spends the morning asking around instead of issuing tools. When something
breaks or never returns, the cost lands on the team with no record to
point to.

ToolCrib keeps a lending register for every workshop tool in Odoo. Each
tool lives in a small catalogue with its reference and condition, and
every loan records the borrower, the date it went out and the date it is
due back. Returning a tool stamps the exact return date and closes the
loan, while open loans show who still holds what and which ones are late.
The cabinet stops being a matter of trust because the register already
knows.

* A catalogue of workshop tools with reference and condition.
* Loans recorded against a borrower with issue and due dates.
* The return stamped with the exact date the tool came back.
* Open loans listed so you see who holds what right now.
* Late loans flagged when the due date has passed.
* One screen to review tools and their lending history.
* A return before the issue date is refused for you.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
    'license': 'OPL-1',
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/tool_crib_tool_0_views.xml',
        'views/tool_crib_loan_1_views.xml',
        'views/tool_crib_open_2_views.xml',
        'views/menus.xml',
        'views/tool_crib_open_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
