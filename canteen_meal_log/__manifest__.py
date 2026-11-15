# -*- coding: utf-8 -*-
{
    'name': 'CanteenLog',
    'version': '20.0.1.0.0',
    'summary': 'Record daily canteen meal services with headcount, costs and notes, confirm logs, and report totals by meal type and period in a company-safe register.',
    'description': '''CanteenLog - Canteen Meal and Service Log
=========================================
Canteen meal counts and costs tracked on paper are hard to reconcile and report.
Daily headcounts and subsidies become unreliable without a consistent log.

CanteenLog provides a structured daily log. Record meal type, headcount and
cost/subsidy details, confirm entries and review totals by period.

* Meal logs with date, meal type and headcount.
* Cost, subsidy and notes per entry.
* States: draft, confirmed.
* Search and reporting by date, meal type and period.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Services',
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
        'data/sequence.xml',
        'views/canteen_meal_log_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
