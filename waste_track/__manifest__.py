# -*- coding: utf-8 -*-
{
    'name': 'WasteWatch',
    'version': '18.0.1.0.0',
    'summary': 'Keep the register of industrial waste collections with the receipts your environmental file requires.',
    'description': '''WasteWatch - Registers Without Drawers
======================================
Industrial waste leaves the site with a paper receipt that ends up in
a drawer. When the environmental file must be produced, the waste
streams, the contractors, the quantities and the proof of collection
are scattered across emails and binders.

WasteWatch keeps one register per waste stream with its code, hazard
class and contracted collector. Every collection is logged with the
date, the quantity, the contractor reference and the receipt number,
and its state follows the collection until the receipt is filed. The
stream totals show how much has been collected and how many receipts
are still pending, so the environmental register is ready on demand.

* A register of waste streams with code, hazard class and contractor.
* Collection logs with date, quantity and contractor reference.
* Receipt numbers kept on every filed collection.
* A workflow from planned to collected and filed.
* Filing refused when the receipt number is missing.
* Stored counters for collections and pending receipts.
* Areas and notes recorded for the environmental file.
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
        'views/wst_stream_0_views.xml',
        'views/wst_collection_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
