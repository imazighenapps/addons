# -*- coding: utf-8 -*-
{
    'name': 'SDSWatch',
    'version': '19.0.1.0.0',
    'summary': 'Keep the current safety data sheet of every chemical product valid and dated, and flag the lapsed ones.',
    'description': '''SDSWatch - Sheets Current Or Flagged
====================================
Every chemical product used on site must be covered by a current safety
data sheet. In practice the PDF sits in a shared folder, the issue date
is handwritten on a cover page and nobody notices when a supplier issues
a new revision or when the validity expires. The first time the gap is
seen is during an inspection or an incident, when the missing sheet is
no longer a document problem but a compliance one.

SDSWatch keeps one Odoo record per chemical product: the supplier, the
hazard class and the current sheet version with its issue and expiry
dates. The current validity and the lapsed flag are computed and stored
so every expired or missing sheet can be filtered and reviewed without
opening a folder. Each revision is logged as a version with its own
dates and reference, and marking one as current rolls the product
forward. Archiving a product keeps its history, while the whole file
stays in the chatter for audits.

* One product register with supplier, hazard class and current version.
* Current sheet issue and expiry dates stored on every product.
* Lapsed and missing flags computed and stored for easy filtering.
* A version history with issue date, expiry date and reference.
* Marking a version current refreshes the product dates.
* Counters for version count stored on the product.
* A sheet whose expiry comes before its issue is refused for you.
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
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/sds_product_0_views.xml',
        'views/sds_version_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
