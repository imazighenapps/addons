# -*- coding: utf-8 -*-
{
    'name': 'QualityInspectionLog',
    'version': '20.0.1.0.0',
    'summary': 'Record product inspections with criteria, observations, results and follow-up notes to keep a traceable quality history.',
    'description': '''QualityInspectionLog - Quality Inspection Register
==================================================
Incoming or in-process checks recorded on paper are hard to trace and audit.

QualityInspectionLog provides a simple, structured inspection record per check
with an explicit result and follow-up.

* Inspection records with product, reference and date.
* Inspector, criteria/notes and observations.
* Pass, fail or pending result with decision notes.
* Draft, in progress, passed, failed and cancelled states.
* Corrective action and follow-up notes.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Inventory',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'product',
        'stock',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/quality_inspection_log_0_views.xml',
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
