# -*- coding: utf-8 -*-
{
    'name': 'LegalArchivePro - Tamper-Evident Legal Document Archive',
    'version': '20.0.1.0.0',
    'summary': 'Keep invoices, bills, contracts and payslips in a tamper-evident archive with SHA-256 hash chaining, retention expiry dates and a complete audit log.',
    'description': '''LegalArchivePro - Tamper-Evident Legal Document Archive
======================================================
Accounting departments are legally required to keep invoices, supplier
bills, contracts and payslips for several years, yet the digital copies
usually sit in random shared folders where anyone can rename, overwrite
or silently edit them. When a tax audit or a litigation asks for the
exact document that was issued on a given date, nobody can prove that
the file was never altered after the fact. LegalArchivePro turns Odoo
into a tamper-evident legal archive. Each document is registered with
its counterparty, its type, its document date and a retention period in
years, and the expiry date is computed automatically. Sealing a
document computes the SHA-256 of its bytes and chains it to the hash of
the previous sealed document of the same company, so the whole archive
forms a single verifiable chain: altering one byte anywhere breaks the
chain and every later verification fails loudly. Every sealing,
verification, archiving and purge operation is written to an audit log
with the user and the date. When the retention period has elapsed, the
file is purged to free storage while the reference, the hash and the
audit log are kept as proof of what the document once was. The module
is multi-company, relies only on the Python standard library and needs
no Enterprise module.

* Central register for invoices, bills, contracts, payslips and other
  documents.
* One-click SHA-256 sealing with hash chaining between documents.
* Verification that detects any modification of the archived file.
* Retention period in years with an automatic expiry date.
* File purge blocked until the retention period has elapsed.
* Immutable audit log covering creation, sealing, verification,
  archiving and purging.
* Multi-company archive with one hash chain per company.
* Searchable and filterable archive with no external Python
  dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Productivity/Document Management',
    'license': 'OPL-1',
    'price': 139.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/archive_document_0_views.xml',
        'views/archive_log_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
