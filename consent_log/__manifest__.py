# -*- coding: utf-8 -*-
{
    'name': 'ConsentBook',
    'version': '20.0.1.0.0',
    'summary': 'Keep the dated proof of every marketing consent, its source and withdrawal, the only defence that counts.',
    'description': '''ConsentBook - Consent You Can Show
==================================
Marketing consent is collected in forms, events and phone calls, then
stored in inboxes and spreadsheets. When a contact asks to be removed
or a regulator asks for proof, nobody can show when the consent was
given, where it came from or when it was withdrawn.

ConsentBook keeps a dated register of every consent with the contact,
the purpose, the channel and the source of proof. Each record is
granted on a precise date and can be withdrawn on another, with the
withdrawal reason kept on file. Active consents are easy to filter,
withdrawn ones remain auditable, and the evidence you need is the
record the module already holds.

* A dated register of marketing consents per contact and purpose.
* Source and channel captured for every consent you collect.
* Granted and withdrawn dates with a written withdrawal reason.
* Active, withdrawn and expired states with a clear audit trail.
* A proof reference or note kept on every record.
* Contact consent counters stored for quick review.
* Multi-company isolation out of the box.
* A defensible history that can be shown when it matters.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/consent_subject_0_views.xml',
        'views/consent_record_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
