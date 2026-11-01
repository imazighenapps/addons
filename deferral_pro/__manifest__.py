# -*- coding: utf-8 -*-
{
    'name': 'DeferralPro',
    'version': '20.0.1.0.0',
    'summary': 'Spread prepaid expenses and deferred revenue over their real period, post one month or the whole schedule, and keep posted and remaining amounts exact.',
    'description': '''DeferralPro - Prepaid Expenses and Deferred Revenue
===================================================
An insurance premium paid in January covers twelve months, but the whole
cost lands in January unless somebody splits it by hand. The same happens
with annual maintenance contracts, rent deposits, licence fees and every
customer invoice billed a year in advance. Accountants then rebuild the
schedule in a spreadsheet, forget one period, and the monthly result stays
wrong until the auditor asks for the detail.

DeferralPro keeps the split inside Odoo. Create a schedule, choose whether
it spreads a prepaid expense or a deferred revenue, enter the total amount
and the period covered, and the module generates one line per month with
rounded amounts whose sum is exactly the total. Start the schedule to
generate the lines, then post them one by one at each closing or all at
once when the period is closed. When a general journal and two accounts are
configured, every posted line creates and posts a balanced journal entry
automatically; without them the line is still flagged as posted so the
schedule remains usable in a light setup. Posted amount and remaining
amount are recomputed after every posting, and the schedule closes itself
once the last period is booked. Cancelling a schedule blocks any further
posting, and a cancelled schedule can be reset to draft as long as no
journal entry has been created. Everything is multi-company, multi-currency
and traced in the chatter.

* Prepaid expense and deferred revenue schedules in a single model.
* Monthly lines generated from the period, rounded so they add up exactly.
* Post one period at a time or the whole schedule in one click.
* Automatic balanced journal entry when a journal and two accounts are set.
* Posted and remaining amounts always up to date.
* Draft, running, done and cancelled states with a full audit trail.
* Reset to draft as long as nothing has been booked.
* Multi-company, multi-currency, no Enterprise dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 119.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/deferral_schedule_0_views.xml',
        'views/deferral_line_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
