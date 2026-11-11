# -*- coding: utf-8 -*-
{
    'name': 'ShrinkWatch',
    'version': '19.0.1.0.0',
    'summary': 'Turn every stock adjustment into a shrinkage analysis by location, product and reason, with the cost attached.',
    'description': '''ShrinkWatch - Losses With Names
===============================
Stock adjustments happen every week, but the story behind them disappears
into a notebook: a broken pallet in aisle B, a picking error on a fast
mover, a count that never matched. Finance only sees a total loss line at
month end, long after anyone can explain where the money went.

ShrinkWatch turns every adjustment into a named shrinkage record. Each
entry captures the location, the product, the reason, the quantity lost and
the unit cost, and the loss value is computed and stored on the spot. Group
the register by location, product or reason to see which corner of the
warehouse costs the most, and keep a dated trail the team can act on instead
of guessing.

* A shrinkage register with product, location and reason on every entry.
* Quantity and unit cost with the loss value computed and stored.
* States to draft, confirm and close each adjustment entry.
* Stored counters and totals ready for filters and analysis views.
* One screen to review confirmed and closed losses by reason.
* Search filters and group-by views for location, product and reason.
* A close date stamped when the entry is finalized.
* Multi-company isolation with per-company records.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Inventory',
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
        'views/shrink_adjustment_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
