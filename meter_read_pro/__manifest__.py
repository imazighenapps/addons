# -*- coding: utf-8 -*-
{
    'name': 'MeterBook',
    'version': '18.0.1.0.0',
    'summary': 'Keep an Odoo register of every electricity, water and gas meter, file the periodic readings in order and see the consumption of each period computed for you.',
    'description': '''MeterBook - Meters Read, Consumption Known
==========================================
The meters are read on a hand-written note that lives in a drawer. The
values are never kept in one place, the readings of two months are taken
twice, and when a bill looks wrong nobody can rebuild the series to
prove what the site really consumed.

MeterBook keeps one Odoo record per meter - electricity, water, gas or
anything else - with its location and its unit. The reader files a dated
reading, the module refuses a second value the same day on the same
meter, and computes the consumption against the previous reading. Each
meter shows its last value, its last date and its count, all the
readings of the company can be grouped by meter, month or reader, and
the whole history stays searchable for the next dispute.

* One record per meter, typed by utility with location and unit.
* Dated readings with the reader who took them.
* One reading per meter and per day, enforced for you.
* Consumption of each period computed and stored.
* Last value, last date and last consumption on the meter.
* Consumption screens grouped by meter or by month.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
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
        'views/meter_0_views.xml',
        'views/meter_reading_1_views.xml',
        'views/meter_consumption_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
