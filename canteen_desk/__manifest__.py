# -*- coding: utf-8 -*-
{
    'name': 'CanteenBook',
    'version': '19.0.1.0.0',
    'summary': 'Tell the caterer each morning how many lunches per team and shut the count at a fixed cut-off time.',
    'description': '''CanteenBook - One Count, No Waste
=================================
The daily lunch count travels by email, sticky notes and last-minute
messages: teams report different numbers, the caterer gets the wrong
headcount and food is wasted or missing. Once service starts, nobody
can say which number was actually sent, and the cut-off is a matter of
habit rather than a rule.

CanteenBook keeps one Odoo record per day and team: the responsible
employee, the number of meals ordered and the cut-off time. When the
count is sent, the record is closed so late changes are visible instead
of silent. A daily total sums the meals across teams for the caterer,
and the register tells you exactly what was ordered on which day.

* A daily headcount per team with responsible employee.
* The number of meals ordered for each team.
* A fixed cut-off time recorded on every count.
* One action to close the count once it is sent to the caterer.
* A daily total of meals computed from the open records.
* A sent count that cannot be edited by mistake.
* Chatter traceability on every headcount.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
    'license': 'OPL-1',
    'price': 39.0,
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
        'views/canteen_count_0_views.xml',
        'views/canteen_draft_1_views.xml',
        'views/menus.xml',
        'views/canteen_draft_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
