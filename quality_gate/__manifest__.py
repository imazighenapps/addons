# -*- coding: utf-8 -*-
{
    'name': 'QualityGate - Quality Control and Inspections',
    'version': '19.0.1.0.0',
    'summary': 'Run incoming, in-process and outgoing quality inspections with reusable control plans, measured checkpoints and tracked non-conformities.',
    'description': '''QualityGate - Quality Control and Inspections
=============================================
Three simple questions: did we check it, did it pass, and what did we do
when it did not?

QualityGate gives Odoo Community a complete quality control workflow. Build
a control plan per operation - incoming, outgoing, internal transfer or
workshop - with the checkpoints that matter: visual pass/fail, measured
value, tolerance range or free text. Start an inspection from a product, a
lot or a transfer and the checkpoints are loaded automatically. Nothing can
be marked as passed while a required checkpoint is missing or out of
tolerance. When something fails, the non-conformity is recorded with its
severity, root cause and corrective action, and the whole story stays in the
chatter.

* Reusable control plans per operation.
* Four checkpoint types: pass/fail, measure, range and text.
* Acceptance limits with a unit of measure.
* Inspections linked to product, lot/serial and transfer.
* Automatic checkpoint loading when the inspection starts.
* Pass blocked until every required checkpoint is validated.
* Non-conformities with severity, root cause and corrective action.
* Full audit trail, multi-company, no Enterprise dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Manufacturing/Manufacturing',
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
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/quality_inspection_plan_0_views.xml',
        'views/quality_inspection_1_views.xml',
        'views/quality_issue_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
