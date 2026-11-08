# -*- coding: utf-8 -*-
{
    'name': 'DeadStock',
    'version': '19.0.1.0.0',
    'summary': 'Spot products that no longer move, measure the cash they lock up and the cost of holding them, and decide discount, bundle, return or scrap from one screen.',
    'description': '''DeadStock - Dormant Inventory Radar
===================================
Every warehouse has them: the pallet nobody has touched since last spring,
the reference that looked like a good deal, the spare part for a machine
the customer replaced. They sit in the racks, they count in the inventory,
and they quietly cost money every day.

DeadStock scans the products that still have stock on hand and looks at the
date of their last customer delivery. A product with no movement for the
number of days set in the rule becomes a dormant line, with the quantity on
hand, the value at standard cost, the number of idle days and the cost of
holding that stock for the period. A suggestion - discount, bundle, return
to supplier, scrap or keep - turns the analysis into an action plan, and
each scan keeps its own snapshot so the progress is measurable.

* Dormant stock detected from the last real customer delivery.
* Configurable idle period and minimum value per company.
* Value at standard cost and cost of holding for the idle period.
* Suggested action: discount, bundle, return, scrap or keep.
* Persistent scan snapshots with totals, for month-to-month comparison.
* Per-warehouse and per-category scope.
* Actioned, ignored and reopen workflow on each line.
* Kanban, graph and pivot, multi-company isolation.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Inventory',
    'license': 'OPL-1',
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'stock',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/dead_stock_line_0_views.xml',
        'views/dead_stock_scan_1_views.xml',
        'views/dead_stock_rule_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
