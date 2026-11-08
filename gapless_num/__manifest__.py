# -*- coding: utf-8 -*-
{
    'name': 'GaplessNum',
    'version': '19.0.1.0.0',
    'summary': 'Detect, trace and block gaps, duplicates and manual renumbering in legal document sequences, with a dated audit journal per journal and company.',
    'description': '''GaplessNum - Legal Numbering Without Gaps
=========================================
A missing invoice number is not a cosmetic defect: on an audit, a gap in a
legal sequence is a question the accountant has to answer in writing. Most
companies discover the gap months later, in a spreadsheet, with no way to
say who removed the number or when.

GaplessNum reads the posted moves of a period, extracts the numeric part of
every legal number, and reports the three things an auditor looks for: a
number that is missing, a number used twice, and a number that no longer
follows the chronological order of the entries. The rules are set per
company and per journal, with a tolerance for the rare legitimate break.
Manual renumbering of a posted entry can be warned or blocked outright, and
every anomaly keeps the move, the expected number, the number found and the
date, so the answer to the auditor is already written.

* Gap detection on any journal and any period, with a configurable tolerance.
* Duplicate and out-of-order detection on the same scan.
* Warn or block a manual change of the number of a posted entry.
* Dated audit journal of every anomaly, linked to the move.
* Resolve, ignore and reopen workflow with a chatter trail.
* Scan wizard that never creates the same anomaly twice.
* Kanban, graph and pivot to read the anomalies by kind and by date.
* Multi-company rules: one company never reads another company's numbering.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 79.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/gapless_issue_0_views.xml',
        'views/gapless_rule_1_views.xml',
        'views/gapless_scan_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
