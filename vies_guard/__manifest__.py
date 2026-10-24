# -*- coding: utf-8 -*-
{
    'name': 'VIESGuard - EU VAT Number Validation',
    'version': '18.0.1.0.0',
    'summary': 'Check every EU VAT number against the official VIES service, keep a dated proof, re-check automatically and audit every result.',
    'description': '''VIESGuard - EU VAT Number Validation
====================================
Stop invoicing a customer whose VAT number is wrong.

VIESGuard connects Odoo to the official European VIES service. When a
partner is created or its VAT number changes, the number is checked and the
result is stored on the partner with the date and the trader name returned by
VIES. Every check is written in an audit trail, so you can prove at any time
that the number was valid on the invoice date. A batch screen checks all your
customers in one click, and a scheduler re-checks the old results.

* Automatic VIES check when a VAT number is created or changed.
* Result stored on the partner: valid, invalid or service unavailable.
* Trader name and address returned by VIES.
* Dated audit trail of every check, manual or automatic.
* Batch check of all customers and suppliers.
* Automatic re-check after a configurable number of days.
* Clear warning on the partner form when a number is invalid.
* Works with Odoo Community and Enterprise, multi-company.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Accounting/Localizations',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/vies_check_0_views.xml',
        'views/vies_batch_wizard_1_views.xml',
        'views/menus.xml',
        'views/partner_inherit.xml',
        'data/cron.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
