# -*- coding: utf-8 -*-
{
    'name': 'AssetPro - Fixed Asset Register and Depreciation',
    'version': '18.0.1.0.0',
    'summary': 'Keep a fixed asset register, generate linear or declining depreciation schedules, post periods and record disposals with gain or loss.',
    'description': '''AssetPro - Fixed Asset Register and Depreciation
================================================
Your fixed assets live in a spreadsheet. The depreciation schedule lives in
another one. Nobody knows the net book value of the fleet, and the auditor
asks for a disposal report you cannot produce.

AssetPro keeps the whole fixed asset register inside Odoo. Each asset carries
its category, its acquisition value, its salvage value and its in-service
date. Validating the asset generates a complete depreciation schedule, month
after month, using the linear method or the declining balance method. Posting
a period marks the due lines as booked and updates the net book value. When
an asset is sold or scrapped, the disposal value is recorded and the gain or
loss is computed against the net book value.

* Asset register with category, supplier, location and responsible.
* Linear and declining balance depreciation methods.
* Automatic monthly schedule generated on validation.
* Post due periods in one click, with a posting date.
* Net book value and remaining depreciable amount, always up to date.
* Disposal with value, date and automatic gain or loss.
* Reset an asset for correction without losing its history.
* Multi-company and multi-currency ready.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 89.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/asset_record_0_views.xml',
        'views/asset_depreciation_line_1_views.xml',
        'views/asset_category_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
