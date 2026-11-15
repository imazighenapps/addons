# -*- coding: utf-8 -*-
{
    'name': 'DonationLog',
    'version': '18.0.1.0.0',
    'summary': 'Record donations with donor, date, amount and purpose, track received and acknowledged states, and report contributions by donor and period in a company-safe register.',
    'description': '''DonationLog - Donation and Contribution Tracking
================================================
Donations tracked in spreadsheets are hard to consolidate and report. Knowing
totals by donor, period and purpose requires manual work.

DonationLog provides a simple donation register. Record each donation with donor,
date, amount and purpose, mark it received and acknowledged, and review totals
by donor and period.

* Donation records with donor, date, amount and purpose.
* Payment method/reference and notes.
* States: draft, received, acknowledged.
* Search and reporting by donor, state and period.
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
        'views/donation_log_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
