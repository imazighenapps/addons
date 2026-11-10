# -*- coding: utf-8 -*-
{
    'name': 'Intrastat',
    'version': '18.0.1.0.0',
    'summary': 'Assemble the intra-EU dispatch and arrival data from your moves and hand the customs office a filing file.',
    'description': '''Intrastat - Flows Filed, Not Guessed
====================================
Intra-EU trade declarations are rebuilt from memory every month: dispatches
live in sales orders, arrivals in purchase receipts, and the customs office
receives a file stitched together at the last minute. Missing country codes,
wrong commodity codes and unvalued lines turn the filing into a correction
cycle nobody can explain.

Intrastat collects every cross-border movement in one declaration per period
and direction. Each flow line records the partner country, the commodity code,
the quantity, the invoice value and the net mass, so the totals the office
expects are computed and stored on the declaration itself. The report moves
from draft to review to filed, and a filed declaration stays locked as the
reference for the period. One screen shows the dispatch and arrival data ready
to hand over instead of guessed.

* Declarations per period and direction, dispatch or arrival.
* Flow lines with partner country, commodity code and net mass.
* Quantity and invoice value recorded on every movement line.
* Stored line count and total value on each declaration.
* Draft, review and filed states with a dated filing stamp.
* Filed declarations locked to preserve the submitted figures.
* A review screen for declarations still waiting to be filed.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/intra_report_0_views.xml',
        'views/intra_flow_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
