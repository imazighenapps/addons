# -*- coding: utf-8 -*-
{
    'name': 'ProvisionBook',
    'version': '20.0.1.0.0',
    'summary': 'Recompute your bad debt and warranty provisions every month and keep an auditable trail of each movement.',
    'description': '''ProvisionBook - Provisions, Recomputed
======================================
Bad debt and warranty provisions are recalculated in a spreadsheet at
month end: the formula changes, a line is overwritten, and the audit
trail of how the balance moved is gone. When the auditor asks why the
provision jumped in March, the answer is a guess.

ProvisionBook keeps every provision and every movement in Odoo. Create
a provision for bad debt, warranty or any other risk, set its opening
balance, then record increases and decreases as dated movements with a
reason. The current balance is recomputed and stored from the movement
history, so the amount on screen always matches the trail. Each
recomputation can be logged, the provision can be closed when the risk
is settled, and nothing can be changed silently. The auditor sees the
movements, not the spreadsheet.

* A register of provisions with type, owner and opening balance.
* Dated movements for every increase and decrease with a reason.
* Current balance computed and stored from the movement history.
* Provision types for bad debt, warranty and other risks.
* Open and closed states with a controlled workflow.
* Movements refused on a closed provision.
* Amounts guarded against impossible values.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
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
        'views/provision_book_0_views.xml',
        'views/provision_movement_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
