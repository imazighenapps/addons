# -*- coding: utf-8 -*-
{
    'name': 'SupplierCert',
    'version': '19.0.1.0.0',
    'summary': 'Keep the ISO, organic, halal or kosher certificates of each supplier alive and block orders when one lapses.',
    'description': '''SupplierCert - Certificates Alive Or Blocked
============================================
Supplier certificates expire quietly: an ISO file in an email, an
organic certificate on a shared drive, a halal proof nobody checked
before placing the next order. When an audit arrives, the company
cannot show which supplier is currently certified, which document is
about to lapse or why a blocked supplier was still used.

SupplierCert keeps one register per supplier certificate in Odoo with
its type, reference, issue and expiry dates and the responsible owner.
Each certificate follows a clear status from draft to valid, expiring
and expired, with renewal actions that record the new validity period.
Open and expiring certificates are easy to review, and the chatter
keeps the evidence trail around renewals and decisions. Buyers can see
at a glance whether a supplier's certificate is alive before relying on
it.

* A certificate register per supplier with type and reference.
* Issue, expiry and reminder dates stored on every certificate.
* Status tracking from draft to valid, expiring, expired and renewed.
* Renewal actions that record a new validity period with history.
* A dedicated view for expiring and expired certificates.
* Responsible ownership and notes kept on the certificate.
* Expiry dates before issue dates are refused for you.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Purchase/Purchase',
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
        'views/cert_document_0_views.xml',
        'views/cert_renewal_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
