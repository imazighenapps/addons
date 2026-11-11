# -*- coding: utf-8 -*-
{
    'name': 'KeyBook',
    'version': '20.0.1.0.0',
    'summary': 'Know exactly who holds which key or badge since when, and chase the ones that never came back.',
    'description': '''KeyBook - Every Key Has An Owner
=================================
Keys and badges move from hand to hand with a signature on a sheet of
paper that disappears into a drawer: when a door must be secured or a
badge deactivated, nobody can say with confidence who holds which key
and since when. Missing keys are noticed weeks later, and the only
record is a crossed-out line on a list nobody trusts.

KeyBook keeps one Odoo register per key or badge: its label, type and
reference, plus the current holder and the date it was issued. When a
key comes back, the return is stamped with the exact date so the
custody chain is complete. An open-custody screen shows every key
still out, making it easy to chase what never came back.

* A register of keys and badges with label, type and reference.
* The current holder and the date each key was issued.
* The return date stamped when a key comes back.
* A clear state from issued to returned.
* One missing-keys screen for everything still out.
* A return before the issue date is refused for you.
* Chatter traceability on every custody record.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
    'license': 'OPL-1',
    'price': 45.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/key_item_0_views.xml',
        'views/key_missing_1_views.xml',
        'views/menus.xml',
        'views/key_missing_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
