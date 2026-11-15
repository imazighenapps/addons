# -*- coding: utf-8 -*-
{
    'name': 'DunningFlow',
    'version': '20.0.1.0.0',
    'summary': 'Define reminder levels with delays and letter texts, then generate dunning letters for overdue customer invoices and track them until payment.',
    'description': '''DunningFlow - Overdue Invoice Dunning Letters
=============================================
Chasing late customers by hand means reminders go out late, unevenly, or not
at all, and nobody can say which invoice was reminded at which level.

DunningFlow turns overdue follow-up into a repeatable process: reminder levels
carry a delay in days and the letter text, and one action builds the letters
for every overdue invoice of the period.

* Reminder levels with delay in days, subject and letter body.
* One action to generate letters for overdue posted customer invoices.
* Letters keep the invoice, due date, residual amount and level.
* States: draft, sent, paid, cancelled, with send date.
* Chatter on each letter for the follow-up trail.
* No duplicate letter for the same invoice and level while it is open.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'account',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/dunning_level_0_views.xml',
        'views/dunning_letter_1_views.xml',
        'views/dunning_generate_2_views.xml',
        'views/menus.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
