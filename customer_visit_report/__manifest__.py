# -*- coding: utf-8 -*-
{
    'name': 'VisitReport',
    'version': '20.0.1.0.0',
    'summary': 'Record structured customer visit reports with purpose, summary, outcomes and follow-up actions, track them through draft/submitted/reviewed states, and report by customer and rep.',
    'description': '''VisitReport - Customer Visit and Field Reports
==============================================
Customer visits generate valuable insights, but outcomes are often lost in notes
and emails. Managers lack a consistent view of what happened and what follow-up
is required.

VisitReport provides a structured visit report linked to the customer and the
responsible employee. Capture purpose, summary, outcomes and next actions, then
track reports through submission and review for clear follow-up.

* Visit reports with customer, responsible, date and purpose.
* Summary, outcomes and follow-up action fields.
* Next-action date and follow-up needed indicator.
* States: draft, submitted, reviewed.
* Search and reporting by customer, responsible and period.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'sale',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/customer_visit_report_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
