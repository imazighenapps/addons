# -*- coding: utf-8 -*-
{
    'name': 'PalletDesk',
    'version': '19.0.1.0.0',
    'summary': 'Keep the account of every returnable pallet lent and owed to each partner, so the transport dispute ends.',
    'description': '''PalletDesk - Every Pallet Counted
=================================
Returnable pallets move back and forth with every delivery, but the balance
with each carrier or customer lives in emails and memory. At month end the
dispute starts: who owes how many pallets, since when, and based on which
movements.

PalletDesk keeps a clear account per partner and a movement log for every
pallet lent or returned. Balances are computed and stored so you can see at
a glance who is in debt and by how much. Each movement is dated, traced and
confirmed, turning pallet disputes into a simple, shared record.

* A pallet account per partner with stored lent, returned and balance.
* A movement log recording pallets lent out or returned.
* States to draft and confirm each pallet movement.
* Confirmation date stamped on validated movements.
* Search filters and group-by views for partner and direction.
* An open-balance view to focus on partners who still owe pallets.
* Notes on accounts and movements for operational context.
* Multi-company isolation with per-company records.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Warehouse and Storage',
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
        'views/pallet_account_0_views.xml',
        'views/pallet_movement_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
