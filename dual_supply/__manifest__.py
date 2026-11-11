# -*- coding: utf-8 -*-
{
    'name': 'DualSupply',
    'version': '19.0.1.0.0',
    'summary': 'Map a second source to every critical product and expose the single-supplier items that can stop your plant.',
    'description': '''DualSupply - Never One Source Away
==================================
Critical products often depend on a single supplier because the alternate was
never qualified or the information lives in someone's head. The risk stays
invisible until that supplier fails and the plant stops. A sourcing review
then turns into a scramble to find out which items have no backup and who
could deliver them instead.

DualSupply keeps one sourcing record per critical product and lists the
suppliers that can provide it. Each supplier entry records whether it is the
primary or an alternate source and whether it is qualified, so the backup is
real and not just a name. The number of qualified sources is computed and
stored on every product, flagging single-source items at once. A single-point
screen shows the critical products that can stop your plant because only one
qualified supplier exists. The sourcing map the buyer needs is the one the
module already holds.

* A sourcing record per critical product with company ownership.
* Supplier entries marked as primary or alternate sources.
* Qualification status tracked on every supplier entry.
* Qualified source count computed and stored per product.
* Single-source products flagged automatically for review.
* A screen focused on products with only one qualified source.
* Each product must keep exactly one primary supplier.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Purchase/Purchase',
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
        'views/dual_product_0_views.xml',
        'views/dual_supplier_1_views.xml',
        'views/dual_product_single_2_views.xml',
        'views/menus.xml',
        'views/dual_product_single_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
