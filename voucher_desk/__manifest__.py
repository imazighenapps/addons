# -*- coding: utf-8 -*-
{
    'name': 'VoucherBook',
    'version': '20.0.1.0.0',
    'summary': 'Compute the meal vouchers each employee earned per working day and hand payroll a clean allocation list.',
    'description': '''VoucherBook - Vouchers Earned To The Day
========================================
Meal vouchers look simple until payroll has to justify how many each
employee earned in a given month. Working days, absences and partial
presences are tracked in different places, and the final allocation is
rebuilt in a spreadsheet that nobody can audit later. One wrong count
becomes a recurring complaint.

VoucherBook keeps one voucher period per company with the daily value
and the working days of the month, then lists one allocation per
employee with the days actually worked. The vouchers earned are
computed and stored from the worked days, so the total allocation is
always ready for payroll. A validated period locks the figures while
keeping the detail visible, and the allocation refuses worked days
above the period calendar. Multi-company isolation keeps each payroll
in its own book.

* A voucher period per month with daily value and working days.
* One allocation per employee with the days actually worked.
* Vouchers earned computed and stored for every allocation.
* A period total computed and stored for payroll handoff.
* Validation that locks the period once the count is agreed.
* Worked days above the period calendar are refused for you.
* Employee-linked allocations ready for payroll export.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Human Resources/Employee',
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
        'security/ir.access.csv',
        'views/voucher_period_0_views.xml',
        'views/voucher_allocation_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
