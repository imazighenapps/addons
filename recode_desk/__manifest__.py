# -*- coding: utf-8 -*-
{
    'name': 'RecodeDesk',
    'version': '18.0.1.0.0',
    'summary': 'Renumber a product once and update every reference that points to it, with a full trace of what moved.',
    'description': '''RecodeDesk - Renumber Without Breaking
======================================
Renumbering a product sounds simple until you realise how many places
still point to the old code: labels, spreadsheets, stored references
and the notes people copied into other systems. A quick find-and-replace
fixes nothing when you cannot prove what changed, when it changed and
which references were actually updated.

RecodeDesk keeps one request per renumbering: the old code, the new
code, the reason and the date you plan to apply it. Each request lists
the references that must move, with their source, old value and the new
value written when the change is applied. Applying the request stamps
the completion date, locks the mapping and posts the full trace in the
chatter so every touched reference is accounted for. You can review what
moved long after the rename without guessing.

* One renumbering request per product code change.
* Old code, new code, reason and planned application date.
* A trace line per reference with source and old/new values.
* Stored counts of total and updated references.
* Apply action that stamps completion and locks the request.
* Full trace posted to the chatter on completion.
* Draft and done states to separate planned from applied changes.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Inventory',
    'license': 'OPL-1',
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/recode_request_0_views.xml',
        'views/recode_line_1_views.xml',
        'views/menus.xml',
        'data/ir_sequence_data.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
