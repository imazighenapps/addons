# -*- coding: utf-8 -*-
{
    'name': 'RelancePro',
    'version': '20.0.1.0.0',
    'summary': 'Escalate overdue customer invoices through dated dunning levels, ready-to-send emails, late fees and a per-customer pause, all traced on the invoice.',
    'description': '''RelancePro - Dunning Ladder for Overdue Invoices
================================================
An invoice is seven days late, then fifteen, then thirty. Somebody means to
call the customer, forgets, and the receivable ages another quarter. The
dunning letters Odoo Enterprise sends are not available in Community, so
the follow-up lives in a spreadsheet that nobody updates.

RelancePro turns the follow-up into a ladder. Each level is a number of days
after the due date, an email template and an optional late fee. The wizard
reads every open customer invoice, finds the highest level it has reached,
skips the customers on pause and the invoices already chased at that level,
then sends the email and writes the trace on the invoice. Nothing is ever
sent twice for the same level, and every message stays in the chatter.

* Dunning ladder by days after the due date, per company.
* One email template per level, editable without code.
* Optional late fee recorded on each dunning line.
* Per-customer pause with an end date and a note.
* Wizard to run the ladder for everyone or for selected customers.
* Dry run to preview who would be chased before sending anything.
* No duplicate: one dunning line per invoice and per level.
* History, status and amount due on every line.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 99.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/dunning_level_0_views.xml',
        'views/dunning_line_1_views.xml',
        'views/dunning_run_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
