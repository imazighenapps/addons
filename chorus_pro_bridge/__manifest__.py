# -*- coding: utf-8 -*-
{
    'name': 'Chorus Pro Bridge',
    'version': '20.0.1.0.0',
    'summary': 'Prepare, submit and track Chorus Pro invoice submissions for French public-sector customers with status follow-up.',
    'description': '''Chorus Pro Bridge - Submit and track public-sector invoices
===========================================================
Supplying the French public sector requires invoices to be deposited and
tracked in Chorus Pro. Teams often manage submissions manually, losing
visibility on statuses, rejections and payment progress.

Chorus Pro Bridge centralizes submission profiles and lets users prepare
invoice deposits linked to customer invoices. Each submission stores the
engagement and service codes, payload snapshot, Chorus reference and a
clear lifecycle (draft, ready, submitted, accepted, rejected, paid). A
status log records every update so accounting and sales can follow public
payments without leaving Odoo.

* Submission profiles with service/recipient settings and environment.
* Deposit records linked to customer invoices and public partners.
* Engagement code, service code and deposit references.
* Lifecycle tracking with rejection reason and payment state.
* Status history log with timestamps and messages.
* Retry/refresh preparation actions for rejected submissions.
* Multi-company, no external Python dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Invoicing',
    'license': 'OPL-1',
    'price': 149.0,
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
        'views/chorus_pro_connection_0_views.xml',
        'views/chorus_pro_submission_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
