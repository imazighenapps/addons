# -*- coding: utf-8 -*-
{
    'name': 'CleanLog',
    'version': '18.0.1.0.0',
    'summary': 'Log cleaning and sanitation tasks by area with scheduled and completion dates, responsible person and status, and keep a company-safe completion record.',
    'description': '''CleanLog - Cleaning and Sanitation Task Log
===========================================
Cleaning tasks tracked on paper are hard to prove and easy to miss. Facilities
teams need a clear record of what was cleaned, when and by whom.

CleanLog provides a task log for cleaning and sanitation. Record planned tasks by
area and date, mark them done or missed with notes, and review completion history
for audits and quality control.

* Cleaning tasks with area, description, date and responsible.
* Scheduled and completion tracking.
* States: planned, done, missed, cancelled.
* Search and reporting by area, state and period.
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
        'hr',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'data/sequence.xml',
        'views/cleaning_log_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
