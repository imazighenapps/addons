# -*- coding: utf-8 -*-
{
    'name': 'FieldCheck',
    'version': '19.0.1.0.0',
    'summary': 'Attach mandatory checklists to field jobs and collect signed step-by-step evidence before closing the visit.',
    'description': '''FieldCheck - Every Step, Signed Off
===================================
Attach mandatory checklists to field jobs and collect signed step-by-step evidence before closing the visit.

Key points:
* Job checklists tracked in a dedicated register.
* Signed steps recorded with clear ownership and dates.
* Job evidence visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Field Service',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/field_checklist_entry_0_views.xml',
        'views/field_checklist_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
