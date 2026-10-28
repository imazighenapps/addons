# -*- coding: utf-8 -*-
{
    'name': 'RenewalRadar - Contract Renewal Management',
    'version': '20.0.1.0.0',
    'summary': 'Track contract end dates, notice periods and renewals, with automatic alerts, renewal history and churn reasons.',
    'description': '''RenewalRadar - Contract Renewal Management
==========================================
Never discover an expired contract after it has expired.

RenewalRadar keeps every service contract, subscription, licence, maintenance
plan and lease in one register. Each contract carries its term, its notice
period and its amount. RenewalRadar computes the renewal date, shows how many
days are left, and a daily scheduler flags every contract that enters its
notice period. Renewing is one click: the term is extended, the history is
written, and the customer relationship continues. When a contract is lost, the
churn reason is recorded so that management can act on it.

* Contract register with type, owner, term and amount.
* Renewal date computed from the end date and the notice period.
* Days left and an expiring flag on every contract.
* Daily scheduler that flags contracts entering their notice period.
* One-click renewal that extends the term and keeps the history.
* Renewal history with action, user, date and note.
* Churn reason to understand why contracts are lost.
* Search filters and grouped views per owner, type and status.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'price': 89.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'sale',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/renewal_contract_0_views.xml',
        'views/renewal_log_1_views.xml',
        'views/menus.xml',
        'data/cron.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
