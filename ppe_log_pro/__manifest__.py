# -*- coding: utf-8 -*-
{
    'name': 'GuardKit',
    'version': '19.0.1.0.0',
    'summary': 'Keep the register of every protective equipment you issue: what each employee received, in which size, when it must be renewed and whether it came back.',
    'description': '''GuardKit - Every Vest, Helmet And Glove Tracked
===============================================
Protective equipment is handed out from a cabinet: gloves one morning,
a helmet the next, and the paper register always says something
different from the cabinet. When the labour inspectorate asks for
proof that every operator received the right equipment with the right
standard, the answer is a drawer. Exchanged gear stays on the shelf
with the employee's name on it, and nobody renews anything on time.

GuardKit keeps one Odoo register per equipment: a helmet, gloves, a
vest, with its category, its EN standard and the renewal period from
your rules. Every issue lists the employee, the size, the quantity and
the date it was handed out, and the renewal date is computed from the
validity of the equipment. A return stamps the exact date the gear
came back, and the open-issues screen shows everything still in
service instead of sitting in a cabinet room. The file the inspector
wants is the one the module already produces.

* A register of protective equipment with category and EN standard.
* A renewal period per equipment, in months.
* Issues with employee, size, quantity and issue date.
* The renewal date computed and stored on every issue.
* Returns stamped with the exact date the gear came back.
* One open-issues screen for everything still in service.
* A return before its issue is refused for you.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
    'license': 'OPL-1',
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/ppe_item_0_views.xml',
        'views/ppe_issue_1_views.xml',
        'views/ppe_open_2_views.xml',
        'views/menus.xml',
        'views/ppe_open_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
