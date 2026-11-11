# -*- coding: utf-8 -*-
{
    'name': 'ForkCheck',
    'version': '18.0.1.0.0',
    'summary': 'Run the daily safety checklist of every forklift and ground the truck until the defect is signed off.',
    'description': '''ForkCheck - Grounded Until Fixed
================================
A forklift rolls out every morning because yesterday's driver scribbled
"OK" on a sheet and nobody read the rest. A worn tyre, a weak brake or a
leaking fork is discovered after the shift, when the truck has already
moved pallets and people all day. The daily checklist exists on paper,
but a defect has no owner, no follow-up and no way to keep the vehicle
off the floor.

ForkCheck keeps the daily safety check of every forklift in Odoo. Each
check records the truck, the operator, the date and the result of the
inspection, and every point that fails becomes a defect with its
description and a sign-off when it is fixed. A truck with an open defect
is grounded on the check, so it cannot be treated as ready for work until
someone signs the repair off. The morning question "is this forklift safe
to drive" has one answer, and it is written down.

* A daily safety check per forklift with operator and date.
* Checklist points recorded on each inspection.
* Defects created with description and repair sign-off.
* Grounded status when a defect remains open.
* Open defects counted and stored on the check.
* One screen to review checks and their defects.
* A repair sign-off without a date is refused for you.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
    'license': 'OPL-1',
    'price': 45.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/forklift_check_0_views.xml',
        'views/forklift_defect_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
