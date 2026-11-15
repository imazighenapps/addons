# -*- coding: utf-8 -*-
{
    'name': 'InspectLog',
    'version': '18.0.1.0.0',
    'summary': 'Log equipment inspections with findings and follow-up actions, track status from planned checks to closure, and keep a company-safe inspection history.',
    'description': '''InspectLog - Equipment Inspection Log
=====================================
Equipment inspections recorded on paper or spreadsheets are hard to track,
leading to missed checks and unresolved findings.

InspectLog provides a structured inspection register. Record equipment, date,
inspector, findings and follow-up actions, and track inspections to closure.

* Inspection records with equipment, date and inspector.
* Findings, condition/result and follow-up actions.
* States: planned, done, issue_found, closed.
* Search and reporting by equipment, inspector and period.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Maintenance/Maintenance',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'maintenance',
        'hr',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/equipment_inspection_log_0_views.xml',
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
