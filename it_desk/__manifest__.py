# -*- coding: utf-8 -*-
{
    'name': 'ITBook',
    'version': '19.0.1.0.0',
    'summary': 'Register every laptop, phone and screen, who uses it, since when and what to do with it when they stop.',
    'description': '''ITBook - Hardware, Owned And Traced
===================================
Laptops leave the IT closet on a handshake, phones are passed around
without a record and screens disappear when someone changes desk.
When a device breaks or an employee leaves, nobody knows who has it,
when it was assigned or whether it ever came back.

ITBook keeps one register per hardware asset with its type, serial
number, purchase date and lifecycle state. Every assignment records
the holder, the handover date and the expected or actual return, so
the current owner is always known. Devices can be marked in stock, in
use, in repair or retired, open assignments are visible at a glance
and the offboarding question is answered by the module, not by email.

* A hardware register with type, serial, model and purchase date.
* Lifecycle states for stock, in use, in repair and retired devices.
* Assignments with holder, handover date and return tracking.
* The current holder kept up to date on each asset.
* Open assignment counters stored on every asset.
* A clear queue of assignments still waiting for a return.
* Multi-company isolation out of the box.
* A full chatter trail for every handover decision.''',
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
        'views/it_asset_0_views.xml',
        'views/it_assignment_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
