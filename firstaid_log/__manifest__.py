# -*- coding: utf-8 -*-
{
    'name': 'FirstAid',
    'version': '18.0.1.0.0',
    'summary': 'Keep every first aid kit complete: what must be inside, what expires when and the refill rounds to run.',
    'description': '''FirstAid - Kits Ready In Seconds
================================
A first aid kit hangs on the wall, but nobody knows whether the bandages
are there, whether the disinfectant expired last year or who is supposed
to refill it. When an incident happens the kit is opened in a hurry and
the missing item is discovered at the worst moment. Refill rounds are
done from memory, so some locations are checked twice and others not at
all.

FirstAid keeps an Odoo register of every first aid kit on site. Each kit
lists the location and the employee responsible for it, and its contents
are tracked as items with the required quantity, the quantity on hand and
the expiry date. A refill round records what was restocked and when, and
the kit shows how many items are missing or expired so the gaps are
visible before anyone needs them. The kit is ready because the register
says so.

* A register of first aid kits with location and responsible.
* Kit contents with required quantity, on hand and expiry date.
* Refill rounds recorded with date and restocked items.
* Missing and expired items counted and stored on the kit.
* A quick view of kits that need attention.
* One screen to review kits and their refill history.
* An on-hand quantity below zero is refused for you.
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
        'views/firstaid_kit_0_views.xml',
        'views/firstaid_item_1_views.xml',
        'views/firstaid_refill_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
