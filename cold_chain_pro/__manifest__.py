# -*- coding: utf-8 -*-
{
    'name': 'ColdChain',
    'version': '18.0.1.0.0',
    'summary': 'Register every cold point of your HACCP plan, log its temperature readings, and let each out-of-range reading be flagged, corrected and traced with a written explanation.',
    'description': '''ColdChain - Every Cold Point Under Watch
========================================
The HACCP plan lives on a laminated sheet next to each cold room. The
operator writes the temperature in a pencil notebook, the values are
transcribed late, and when an auditor asks for the readings of the last
nine months with the correction of every breach, nobody can produce a
clean file. A fridge that drifts for a weekend is discovered the day the
stock smells wrong.

ColdChain turns each fridge, cold room and freezer into an Odoo cold
point with a safe range and a check frequency. Every reading is typed
with the operator and the exact moment it was taken, and the range check
is instant: an out-of-range reading is never a detail to remember, it is
a breach in its own screen until it is corrected with a written
explanation. The points display their counters live, the archive keeps
the history without cluttering the daily work, and the whole file is
ready for the audit.

* Cold points with a safe range, a reference and a location.
* Readings checked instantly against the range of their point.
* One Open Breaches screen, the list to empty before the audit.
* Corrections stamped with the note of what was done.
* Live counters of readings and open breaches per point.
* Points and readings grouped by frequency, site and responsible.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Inventory',
    'license': 'OPL-1',
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/cold_point_0_views.xml',
        'views/cold_reading_1_views.xml',
        'views/cold_breach_2_views.xml',
        'views/menus.xml',
        'views/cold_breach_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
