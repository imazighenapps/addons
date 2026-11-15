# -*- coding: utf-8 -*-
{
    'name': 'SupplierVisit',
    'version': '19.0.1.0.0',
    'summary': 'Record supplier visits with purpose, findings and follow-up actions, track reports through submission and review, and keep a company-safe visit history per supplier.',
    'description': '''SupplierVisit - Supplier Visit and Audit Log
===========================================
Supplier visit findings captured in emails or notes are hard to consolidate and
act on. Follow-up actions get missed and supplier history remains fragmented.

SupplierVisit provides a structured visit report linked to the supplier. Record
purpose, attendees, findings and follow-up actions, then review reports so
improvements are tracked.

* Visit reports with supplier, date, purpose and attendees.
* Findings, risks and follow-up actions.
* States: draft, submitted, reviewed.
* Search and reporting by supplier, responsible and period.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Purchase',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'purchase',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/supplier_visit_log_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
