# -*- coding: utf-8 -*-
{
    'name': 'LostFound',
    'version': '20.0.1.0.0',
    'summary': 'Log found items with description, date and location, track claimant and return or disposal status, and keep a searchable lost-and-found register.',
    'description': '''LostFound - Lost and Found Item Register
========================================
Found items logged on paper or not at all are hard to match with owners. Staff
waste time answering enquiries and unclaimed items accumulate.

LostFound provides a structured register for lost-and-found items. Record what was
found, where and when, store claimant details when someone comes forward, and
track whether the item was returned or disposed.

* Items with description, found date, location and finder reference.
* Storage and claimant details.
* States: found, claimed, returned, disposed.
* Search and reporting by state, date and location.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Services',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/lost_found_item_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
