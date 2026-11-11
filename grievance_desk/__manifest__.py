# -*- coding: utf-8 -*-
{
    'name': 'GrievanceDesk',
    'version': '18.0.1.0.0',
    'summary': 'Log employee grievances confidentially with steps, owners and outcomes so sensitive cases are handled properly.',
    'description': '''GrievanceDesk - Cases Handled With Care
=======================================
Log employee grievances confidentially with steps, owners and outcomes so sensitive cases are handled properly.

Key points:
* Cases opened tracked in a dedicated register.
* Case steps recorded with clear ownership and dates.
* Resolutions visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Human Resources/Employee',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/grievance_desk_entry_0_views.xml',
        'views/grievance_desk_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
