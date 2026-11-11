# -*- coding: utf-8 -*-
{
    'name': 'ClockWatch',
    'version': '18.0.1.0.0',
    'summary': 'Detect missing punches, impossible hours and attendance anomalies and route them for correction each day.',
    'description': '''ClockWatch - Punches That Add Up
================================
Detect missing punches, impossible hours and attendance anomalies and route them for correction each day.

Key points:
* Clock events tracked in a dedicated register.
* Missing punches recorded with clear ownership and dates.
* Anomaly queue visible so nothing slips through.
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
        'views/attendance_anomaly_entry_0_views.xml',
        'views/attendance_anomaly_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
