# -*- coding: utf-8 -*-
{
    'name': 'CustomsDesk',
    'version': '19.0.1.0.0',
    'summary': 'Keep HS codes and duty rates on your imported products and check every customs entry against them.',
    'description': '''CustomsDesk - Duty Checked Per Entry
====================================
Import duty is recomputed on every entry from a spreadsheet of HS codes and
rates that nobody keeps current. A wrong code, an outdated rate or a miskeyed
customs value turns a cleared shipment into a back duty claim months later, and
the broker bill is paid because there is no reference to check it against.

CustomsDesk keeps the duty reference in Odoo: each HS code carries its duty
rate and can be reused across entries. A customs entry records the supplier,
the origin country, the declaration date and one line per imported item with the
HS code, the customs value and the quantity. The duty amount of every line and
the total duty of the entry are computed and stored, so the amount you expect
matches the amount you are billed. Checked and cleared entries are locked, and
the register shows what is still waiting to be verified.

* A register of HS codes with the applicable duty rate.
* Customs entries with supplier, origin country and declaration date.
* Entry lines with HS code, customs value and quantity.
* Stored duty amount per line and total duty per entry.
* Draft, checked and cleared states with a dated clearance.
* Cleared entries locked to preserve the declared amounts.
* A screen for entries still waiting to be checked.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
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
        'views/customs_duty_code_0_views.xml',
        'views/customs_entry_1_views.xml',
        'views/customs_entry_line_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
