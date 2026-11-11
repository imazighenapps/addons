# -*- coding: utf-8 -*-
{
    'name': 'CylinderDesk',
    'version': '19.0.1.0.0',
    'summary': 'Track every rented gas cylinder received, emptied and returned, so the supplier bill matches reality.',
    'description': '''CylinderDesk - Cylinders Billed Fairly
======================================
Rented gas cylinders come in, sit in the yard, get swapped, and the
supplier invoice shows a count nobody on site can explain. Empties pile
up behind the full ones, returns are guessed from memory, and the rental
charge keeps running on cylinders that left the premises weeks ago.

CylinderDesk keeps one Odoo register per cylinder type: gas, capacity
and the rental rate your supplier charges. Every custody movement
records the supplier, the quantity received, the date it arrived and the
quantity returned, so the balance still on site is computed for you. The
return date is stamped when the cylinders leave, and open custody lines
show exactly what is still billable instead of what the invoice claims.
When the supplier bill arrives, the numbers on the desk already agree.

* A register of cylinder types with gas, capacity and rental rate.
* Custody movements with supplier, received and returned quantities.
* The on-site balance computed and stored on every custody line.
* A return date stamped when the cylinders leave the yard.
* One open-custody screen for everything still billable on site.
* A return quantity above what was received is refused for you.
* A negative received quantity is refused for you.
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
        'views/cylinder_type_0_views.xml',
        'views/cylinder_custody_1_views.xml',
        'views/cylinder_open_2_views.xml',
        'views/menus.xml',
        'views/cylinder_open_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
