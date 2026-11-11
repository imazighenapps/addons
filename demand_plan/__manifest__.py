# -*- coding: utf-8 -*-
{
    'name': 'ForecastBook',
    'version': '18.0.1.0.0',
    'summary': 'Let each salesperson commit a monthly forecast per product and compare it with real sales, month after month.',
    'description': '''ForecastBook - Commit, Then Compare
===================================
Sales forecasts live in personal spreadsheets: each salesperson commits a
number in a different file, nobody compares it with what was really sold
and the plan is rebuilt from memory every month. When a product misses, the
team argues about the forecast instead of learning from the gap.

ForecastBook gives salespeople one Odoo register per monthly plan. Each
plan names the salesperson, the month and the committed quantity and
revenue per product line, and records the actuals next to the promise so
the variance is computed for you. Plans move from draft to committed and
can be closed once the month is reviewed, with every figure kept for the
next cycle. Managers read the biggest misses on one screen instead of
chasing spreadsheets.

* Monthly forecast plans per salesperson with a clear period.
* Forecast lines per product with committed quantity and revenue.
* Actual quantity and revenue recorded next to every commitment.
* Variance quantity and revenue computed and stored per line.
* A simple workflow from draft to committed to closed.
* Plan totals computed from the forecast lines.
* Closing a plan without lines is refused for you.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/demand_plan_0_views.xml',
        'views/demand_plan_line_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
