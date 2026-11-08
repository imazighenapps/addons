# -*- coding: utf-8 -*-
{
    'name': 'FieldWatch',
    'version': '18.0.1.0.0',
    'summary': 'Turn Odoo native tracking into a readable audit journal: who changed which field, when, from what to what, filterable by model, user and date.',
    'description': '''FieldWatch - Field Change Audit Trail
=====================================
Odoo already tracks the fields you mark as tracked, but the value lives in
a chatter message, buried under notes and emails. When a price, a credit
limit or an address changes, the question is simple - who did it, when, and
what was the value before - and the answer takes ten minutes of scrolling.

FieldWatch collects the native tracking values into its own journal. Pick
the models to watch, optionally the fields, and run the collector on any
period: every change becomes one line with the old value, the new value,
the user, the date and the record. The journal is searchable by model, by
user and by field, exportable, and it keeps a reviewed or ignored status so
the auditor's work is visible. Nothing is duplicated when the same period
is collected twice, and no core model is overridden.

* Journal built from Odoo native tracking, no core model override.
* One line per changed field, with the old and the new value.
* Watch rules by model, with an optional list of fields.
* Collector by period, by model and by rule.
* Search and group by model, user, field and date.
* Reviewed, ignored and reopen workflow.
* Idempotent: the same change is never collected twice.
* Kanban, graph and pivot, multi-company isolation.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Tools/Audit',
    'license': 'OPL-1',
    'price': 119.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/field_watch_log_0_views.xml',
        'views/field_watch_rule_1_views.xml',
        'views/field_watch_collect_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
