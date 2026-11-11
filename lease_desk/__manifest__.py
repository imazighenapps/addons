# -*- coding: utf-8 -*-
{
    'name': 'LeaseBook',
    'version': '20.0.1.0.0',
    'summary': 'Keep the payment schedule of every lease and generate the monthly entry without the spreadsheet errors.',
    'description': '''LeaseBook - Leases Run Themselves
=================================
Leases are easy to sign and hard to track: the payment schedule lives
in the contract PDF, the monthly amount is copied into a spreadsheet,
and a missed indexation or a forgotten payment shows up months later as
a surprise variance.

LeaseBook keeps every lease and its payment schedule in Odoo. Register
the lease with its partner, start and end dates and monthly amount,
then generate a dated schedule of payments covering the full term. As
each month passes, mark the payment as posted with one action and keep
the posted and remaining amounts in view. The schedule is computed
from the lease terms, so the monthly entry is the same every time and
no line is typed by hand. When the lease ends, close it with a full
history of what was paid and what remains.

* A register of leases with partner, term and monthly amount.
* Automatic generation of a dated payment schedule for the term.
* Posted and remaining amounts computed and stored on the lease.
* One-click posting of each monthly schedule line.
* Running and closed states with a controlled workflow.
* Guards that refuse duplicate generation or impossible dates.
* Schedule lines protected once the lease is closed.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 89.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/lease_contract_0_views.xml',
        'views/lease_schedule_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
