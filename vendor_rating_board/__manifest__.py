# -*- coding: utf-8 -*-
{
    'name': 'VendorBoard',
    'version': '18.0.1.0.0',
    'summary': 'Record periodic supplier evaluations with criteria scores, an overall rating, comments and follow-up states to compare vendor performance over time.',
    'description': '''VendorBoard - Supplier Evaluation Scorecard
===========================================
Supplier performance feedback often stays in emails and memory, making it hard
to compare vendors or justify decisions.

VendorBoard provides a simple scorecard per supplier and period with explicit
criteria scores, an overall score and a tracked evaluation state.

* Evaluation records per supplier with period and evaluation date.
* Criteria scores for delivery, quality, price and service.
* Overall score computed from criteria.
* Draft, validated and archived states.
* Comments, strengths and improvement actions.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Purchase',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'contacts',
        'purchase',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/vendor_evaluation_0_views.xml',
        'views/menus.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
