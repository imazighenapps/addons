# -*- coding: utf-8 -*-
{
    'name': 'GaugeBook',
    'version': '18.0.1.0.0',
    'summary': 'Never measure with an overdue instrument: the calibration calendar follows each gauge and blocks the lapsed.',
    'description': '''GaugeBook - Only Fresh Instruments
==================================
A gauge is only trustworthy for as long as its calibration is fresh. In
most workshops the certificate lives in a binder, the next due date is
copied into a spreadsheet and a lapsed instrument keeps measuring until
an audit, a customer complaint or a failed batch proves it was overdue.
Nobody can say, on the day of use, which gauge is safe and which one
must stay on the shelf.

GaugeBook keeps one Odoo record per instrument: the serial number, the
location, the calibration interval and the reference of its last
certificate. The next due date is computed and stored from the last
calibration so every overdue gauge can be filtered and grouped without
a spreadsheet. Each calibration is logged with its date, result and
certificate, and confirming it rolls the instrument forward to a fresh
due date. Blocking a lapsed gauge is explicit and traced in the chatter,
so the only instruments in service are the ones you can trust.

* One instrument register with serial number, location and interval.
* Next calibration due date computed and stored on every instrument.
* Calibration history with date, result, certificate and technician.
* Confirming a calibration refreshes the instrument due date.
* Blocked and in-service states with an explicit lapsed flag.
* Counters for calibration count and overdue status, stored for filters.
* A calibration before the instrument date is refused for you.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
    'license': 'OPL-1',
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/calib_instrument_0_views.xml',
        'views/calib_event_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
