# -*- coding: utf-8 -*-
{
    'name': 'Clearance',
    'version': '19.0.1.0.0',
    'summary': 'Force a documented line clearance between two runs: nothing restarted while the previous product lingers.',
    'description': '''Clearance - Lines Start Clean
=============================
Changeovers fail quietly when the line is restarted with residues of
the previous run: labels, components or product left in place. Without
a documented clearance, the next batch starts on assumptions instead
of evidence and the quality file has nothing to show.

Clearance records each line changeover with the outgoing and incoming
products, the area and the planned restart time. A checklist of
clearance items captures what must be removed, cleaned or verified,
and each item is signed off by a user with a timestamp. The clearance
is released only when every required item is completed, so the line
starts clean and the proof is kept.

* A register of line clearances for every changeover.
* Outgoing and incoming products recorded on each clearance.
* Checklist items for removal, cleaning and verification.
* Sign-off per item with user and completion state.
* Release blocked until every required item is done.
* Stored counters for total and completed items.
* Areas and planned restart times tracked on the record.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/clc_check_0_views.xml',
        'views/clc_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
