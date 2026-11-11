# -*- coding: utf-8 -*-
{
    'name': 'QuarantineDesk',
    'version': '19.0.1.0.0',
    'summary': 'Move doubtful stock into a visible quarantine workflow instead of a note, and decide keep, return or scrap.',
    'description': '''QuarantineDesk - Doubt Never Ships
==================================
A damaged box, a missing label, a temperature doubt: the stock is pushed to
the side of the rack with a sticky note and forgotten. Weeks later the same
goods ship by mistake or sit there with no decision and no owner.

QuarantineDesk gives doubtful stock a visible workflow. Each case records
the product, the lot, the quantity and the reason it was held, then moves
through quarantine until a clear decision is taken: release it, return it or
scrap it. Decision dates and notes are stamped on the record so everyone can
see what happened and why, and the warehouse never ships uncertainty again.

* A quarantine register with product, lot, quantity and hold reason.
* A clear workflow to quarantine, release, return or scrap each case.
* Decision date and note captured on every resolved case.
* Stored counters and status ready for filters and reviews.
* One screen focused on stock still held in quarantine.
* Search filters and group-by views for reason and status.
* Reopen action to move a resolved case back under review.
* Multi-company isolation with per-company records.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Warehouse and Storage',
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
        'views/quarantine_case_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
