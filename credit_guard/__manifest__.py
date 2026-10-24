# -*- coding: utf-8 -*-
{
    'name': 'CreditGuard - Customer Credit Control',
    'version': '18.0.1.0.0',
    'summary': 'Live credit limits for every customer, with automatic blocking of over-limit orders and a controlled override workflow.',
    'description': '''CreditGuard - Customer Credit Control
=====================================
Stop shipping to customers who no longer pay.

CreditGuard gives every customer a live credit limit. It adds open invoices,
unpaid balances and confirmed orders to show the real exposure, then blocks
the order that would push the account over the limit. When a manager decides
to take the risk, a documented override is requested, approved and traced.

* One credit profile per customer: limit, exposure, available amount, usage.
* Automatic exposure from open customer invoices and confirmed orders.
* Overdue amount and overdue days, refreshed in real time.
* Two control modes: warn the salesperson, or block the confirmation.
* Override request workflow: request, approve, refuse, with full audit trail.
* A clear banner on the quotation when the customer is blocked.
* Multi-company and multi-currency ready.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 79.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'sale',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/credit_profile_0_views.xml',
        'views/credit_override_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
