# -*- coding: utf-8 -*-
{
    'name': 'OfficeStock',
    'version': '19.0.1.0.0',
    'summary': 'Keep the small consumables of every office ordered in time without the endless emergency shopping trips.',
    'description': '''OfficeStock - No More Emergency Shopping
========================================
Pens, paper, coffee and toner run out one office at a time: someone
notices at the worst moment, a rushed order is placed, and nobody knows
what is already on the shelf or what the minimum level should be. The
same consumable is bought twice while another office waits, and the
monthly spend is a surprise every time.

OfficeStock keeps one Odoo register per office supply: the item, the
location, the quantity on hand and the minimum level that should trigger
a restock. Restock requests record how much is needed, when it was asked
for and when it was ordered, so the on-hand quantity and the shortage
are computed for you. Pending requests show what must be bought before
it becomes an emergency, and the list of items below minimum gives the
buyer one clear shopping view. The small things stay stocked without the
last-minute run.

* A register of office supplies with location, on-hand quantity and minimum.
* Restock requests with requested quantity, request date and order date.
* The shortage computed and stored on every supply item.
* Pending and ordered states tracked on every restock request.
* One restock-needed screen for items below their minimum level.
* A negative on-hand quantity is refused for you.
* A negative requested quantity is refused for you.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
    'license': 'OPL-1',
    'price': 29.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/office_supply_0_views.xml',
        'views/office_restock_1_views.xml',
        'views/office_restock_needed_2_views.xml',
        'views/menus.xml',
        'views/office_needed_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
