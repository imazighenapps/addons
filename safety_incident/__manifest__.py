# -*- coding: utf-8 -*-
{
    'name': 'SafetyReport',
    'version': '20.0.1.0.0',
    'summary': 'Log workplace safety incidents with date, location, type, severity and corrective actions, track status from report to closure, and report incidents in a company-safe register.',
    'description': '''SafetyReport - Workplace Safety Incident Log
============================================
Safety incidents reported by email or paper are hard to track consistently.
Details, severity and corrective actions get lost, delaying follow-up and review.

SafetyReport provides a structured incident register. Record what happened, where,
who was involved and how severe it was, then track corrective actions and status
until the incident is closed.

* Incident reports with date, location, type and severity.
* Reporter, description and people involved.
* Corrective actions and follow-up notes.
* States: draft, reported, in progress, closed.
* Search and reporting by type, severity, state and period.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Human Resources/Employee',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'hr',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'views/safety_incident_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
