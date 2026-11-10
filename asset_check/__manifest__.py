# -*- coding: utf-8 -*-
{
    'name': 'AssetCheck',
    'version': '19.0.1.0.0',
    'summary': 'Count fixed assets on the floor with tags and statuses, and reconcile the register with what really exists.',
    'description': '''AssetCheck - Fix What Exists, Cancel The Rest
=============================================
The fixed asset register says the company owns equipment that left the building
years ago, while assets bought last quarter never appear in it. The yearly
count happens on a clipboard: tags are scribbled, locations guessed, and the
reconciliation with the accounting register is a spreadsheet nobody trusts.

AssetCheck runs a physical count campaign against a list of expected assets.
Each count line carries the asset tag, the expected location and the result of
the floor check: found, missing or moved, with the location where it was seen.
Counts of found, missing and moved assets are stored on the campaign, so the
gaps are visible before the register is adjusted. Closing the campaign freezes
the results as the evidence of what was physically verified, and the screen of
open campaigns shows which counts are still waiting to be finished.

* Physical asset count campaigns with a planned date and owner.
* Count lines with asset tag, description and expected location.
* Found, missing and moved results with the observed location.
* Stored totals for found, missing and moved assets per campaign.
* Draft, in progress and closed states with a dated close.
* Closed campaigns locked to preserve the verified results.
* One screen for campaigns still in progress on the floor.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
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
        'views/asset_inventory_0_views.xml',
        'views/asset_inventory_line_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
