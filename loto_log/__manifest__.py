# -*- coding: utf-8 -*-
{
    'name': 'LockOut',
    'version': '20.0.1.0.0',
    'summary': 'Run lockout/tagout properly: who locked the machine, why, and who restored it, with no gap in the trace.',
    'description': '''LockOut - Locked, Tagged, Restored
==================================
Lockout and tagout lives on paper tags and memory: a machine is locked
for maintenance, the tag shows a name, and nobody can say with
confidence who isolated it, why it was isolated or who restored power.
When an audit asks for the trace, the answer is a clipboard at the
control panel. Gaps between lock and restore are exactly where serious
incidents happen.

LockOut keeps one Odoo record per lockout: the equipment, the tag
holder, the reason and the moment it was locked. The restoration stamps
who brought the machine back and when, so the full chain is visible on
a single screen. Open lockouts stay in view until they are restored,
and every action is recorded without relying on a paper tag that can
fall off.

* A register of lockouts with equipment, tag holder and reason.
* The lock date recorded when the isolation starts.
* The restore date and restorer stamped on every restoration.
* A clear state from locked to restored.
* One open-lockouts screen for everything still isolated.
* A restoration before the lock date is refused for you.
* Chatter traceability on every lockout record.
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
        'security/ir.access.csv',
        'views/loto_lockout_0_views.xml',
        'views/loto_open_1_views.xml',
        'views/menus.xml',
        'views/loto_open_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
