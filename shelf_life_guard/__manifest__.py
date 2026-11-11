# -*- coding: utf-8 -*-
{
    'name': 'ShelfLife',
    'version': '20.0.1.0.0',
    'summary': 'Guard the shelf life of every perishable lot, push the oldest to the front and warn before dates expire.',
    'description': '''ShelfLife - Oldest Out First
============================
Perishable stock expires in silence: lots sit in the back of the rack,
the receipt date is forgotten and the first warning comes when a
customer returns a product past its date. FEFO rules exist on paper,
but the team has no single view of what expires next and what is
already too old to ship.

ShelfLife keeps a dated register of perishable lots in Odoo with the
product, location, received date, expiry date and quantity still on
hand. The module computes the remaining shelf life in days and stores a
status so expiring and expired lots stand out immediately. Teams can
quarantine a risky lot, mark it consumed or disposed and keep notes on
the decision. The expiry clock, the quantity and the action taken stay
on the same record.

* A perishable lot register with product, location and quantity.
* Received and expiry dates stored on every lot.
* Remaining shelf life computed and stored in days.
* Status tracking for fresh, expiring, expired, quarantined and closed lots.
* Actions to quarantine, consume or dispose of risky stock.
* One screen focused on lots expiring soon or already expired.
* Expiry before receipt is refused for you.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Warehouse and Storage',
    'license': 'OPL-1',
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/shelf_lot_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
