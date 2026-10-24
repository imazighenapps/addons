# -*- coding: utf-8 -*-
{
    'name': 'SubsFlow - Subscriptions and Recurring Invoicing',
    'version': '19.0.1.0.0',
    'summary': 'Recurring subscriptions for Odoo Community: plans, periods, prorata, automatic invoices, pause, MRR and churn.',
    'description': '''SubsFlow - Subscriptions and Recurring Invoicing
================================================
Sell recurring services in Odoo Community, without Enterprise.

SubsFlow manages the full subscription cycle: a plan, a customer, a start
date and a period. Every period, the invoice is created automatically. You
can pause a subscription, resume it, close it, and follow your MRR and churn
on the dashboard.

* Subscription plans with monthly, quarterly or yearly periods.
* Automatic invoice generation through a daily scheduler.
* Prorata on the first period.
* Pause, resume and close with a full audit trail.
* MRR, ARR and churn indicators.
* One click "Invoice now" for exceptional cases.
* Multi-company and multi-currency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Sales/Sales',
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
        'views/subs_subscription_0_views.xml',
        'views/subs_plan_1_views.xml',
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
