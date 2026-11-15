# -*- coding: utf-8 -*-
{
    'name': 'HazardReportLog',
    'version': '18.0.1.0.0',
    'summary': 'Record hazard observations with location, severity, responsible person and resolution states to track risks to closure.',
    'description': '''HazardReportLog - Workplace Hazard Report Register
==================================================
Hazards and near-miss observations reported informally are easy to lose and
hard to close.

HazardReportLog provides a simple register to report, assign and resolve
workplace hazards.

* Hazard reports with date, location, reporter and description.
* Hazard type and severity.
* Responsible person and corrective action notes.
* Draft, reported, in progress, resolved and dismissed states.
* Resolution date and outcome notes.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Project',
    'license': 'OPL-1',
    'price': 29.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'hr',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/hazard_report_log_0_views.xml',
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
