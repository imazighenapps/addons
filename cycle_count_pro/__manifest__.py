# -*- coding: utf-8 -*-
{
    'name': 'CycleCountPro - Inventory Cycle Counting',
    'version': '20.0.1.0.0',
    'summary': 'Plan ABC cycle counts, count by location, control variances and post stock adjustments without freezing the warehouse.',
    'description': '''CycleCountPro - Inventory Cycle Counting
========================================
Stop freezing the warehouse for a full inventory once a year.

CycleCountPro lets you count a small set of products every day, week or
month, compare the counted quantity with the theoretical stock, explain
the variance and post the adjustment in one click. Your stock accuracy
goes up, your operations never stop.

* Count plans per warehouse, with frequency and responsible.
* Sessions generated from a plan, with theoretical quantities prefilled.
* Count by product and location, with variance in quantity and value.
* Variance review before posting the adjustment.
* Automatic stock adjustment through standard Odoo quants.
* Full history of sessions, counters and adjustments.
* Scheduled session creation with a cron.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Inventory/Inventory',
    'license': 'OPL-1',
    'price': 79.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'stock',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/cycle_count_session_0_views.xml',
        'views/cycle_count_plan_1_views.xml',
        'views/cycle_count_line_2_views.xml',
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
