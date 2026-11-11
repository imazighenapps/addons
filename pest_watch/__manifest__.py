# -*- coding: utf-8 -*-
{
    'name': 'PestWatch',
    'version': '20.0.1.0.0',
    'summary': 'Log the pest control stations of the site: checks, findings and the contractor visits the HACCP file wants.',
    'description': '''PestWatch - Stations Checked, Traced
====================================
Pest control lives on a wall map and a stack of contractor visit
reports. Each station has a number, a location and a check frequency,
but the last inspection date is buried in a PDF and the findings are
scattered across emails. When the HACCP auditor asks for the station
log, the evidence must be rebuilt from paper instead of read from one
screen.

PestWatch keeps one Odoo record per monitoring station: its code, its
location, the station type and the check interval you follow. The next
check date and the overdue flag are computed and stored so every late
station can be filtered without a spreadsheet. Each inspection is logged
with its date, its findings and the contractor reference, and confirming
an inspection rolls the station forward to its next due date. Findings
and corrective notes stay on the record, and the full history remains in
the chatter for the HACCP file.

* One station register with code, location, type and check interval.
* Next check date and overdue flag computed and stored on every station.
* Inspection history with date, findings, severity and contractor.
* Confirming an inspection refreshes the station next due date.
* Active and out-of-service states with an audit trail.
* Counters for inspection count and open findings stored for filters.
* An inspection dated in the future is refused for you.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
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
        'views/pest_station_0_views.xml',
        'views/pest_inspection_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
