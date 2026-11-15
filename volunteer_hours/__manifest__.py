# -*- coding: utf-8 -*-
{
    'name': 'VolunteerLog',
    'version': '18.0.1.0.0',
    'summary': 'Log volunteer hours with volunteer, date, hours and activity, validate submitted entries, and report time by volunteer and period in a company-safe register.',
    'description': '''VolunteerLog - Volunteer Hours Tracking
=======================================
Volunteer contributions tracked by email or paper are hard to total and report.
Coordinators need a consistent record of who contributed, when and for how long.

VolunteerLog provides a simple hours register. Record entries with volunteer, date,
hours and activity, submit and validate them so totals can be reported by
volunteer and period.

* Volunteer hour entries with volunteer, date, hours and activity.
* Notes and optional reference.
* States: draft, submitted, validated.
* Search and reporting by volunteer, state and period.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Services',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/volunteer_hours_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
