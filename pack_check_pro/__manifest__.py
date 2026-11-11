# -*- coding: utf-8 -*-
{
    'name': 'PackCheck',
    'version': '18.0.1.0.0',
    'summary': 'Verify weight and piece count on the packing bench before the box leaves, with a log the claims team can trust.',
    'description': '''PackCheck - Checked Before It Leaves
====================================
A box leaves the bench with a handwritten note, a guessed weight and a piece
count nobody double checked. When the carrier disputes the shipment or the
customer claims a shortage, there is no proof of what was actually packed.

PackCheck brings a simple control to the packing bench. Each check records
the expected and actual weight and piece count, computes the variance and
marks the result as passed or failed. Approved checks form a trusted log the
claims team can rely on, and every rejected box is visible before it leaves
the building.

* A packing check register with expected and actual weight and count.
* Variance and pass or fail result computed and stored on each check.
* A workflow to draft, verify, approve or reject every packing check.
* A decision date stamped when a check is approved or rejected.
* Search filters and group-by views for result and status.
* A dedicated log view of approved checks for claims follow-up.
* Notes to capture issues found at the packing bench.
* Multi-company isolation with per-company records.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Warehouse and Storage',
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
        'views/pack_check_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
