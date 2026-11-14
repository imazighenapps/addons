# -*- coding: utf-8 -*-
{
    'name': 'CheckFlow',
    'version': '20.0.1.0.0',
    'summary': 'Define reusable checklist templates, run them on jobs with per-item results and notes, and track completion progress and outcomes in a company-safe, reportable register.',
    'description': '''CheckFlow - Reusable Service and Job Checklists
===============================================
Recurring jobs rely on technicians remembering every step. Without a standard
checklist, steps are skipped, quality varies and completion is hard to prove.

CheckFlow lets managers define reusable checklist templates with ordered items.
Each job instantiates a checklist run from a template; technicians mark every
item as done, failed or not applicable and add notes. Completion progress and
overall state are computed so managers can review outcomes by template and period.

* Reusable checklist templates with ordered items per company.
* Checklist runs created from templates with a job/reference label.
* Per-item results: to do, done, failed, not applicable, with notes.
* Computed completion progress and overall run state.
* Search and reporting by template, responsible, state and period.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Services',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/service_checklist_run_0_views.xml',
        'views/service_checklist_template_1_views.xml',
        'views/service_checklist_run_line_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
