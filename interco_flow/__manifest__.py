# -*- coding: utf-8 -*-
{
    'name': 'InterCo Flow',
    'version': '19.0.1.0.0',
    'summary': 'Turn a confirmed sales order into the matching purchase order in another company of the group, with product mapping, transfer margin and a traced link on both sides.',
    'description': '''InterCo Flow - Automated Intercompany Trading
=============================================
A group sells through several companies. The customer orders from the sales
company, the goods leave the warehouse of the sister company, and somebody
retypes the same order as a purchase order on the other side. One forgotten
line, one price that does not match, and the group margin disappears in a
consolidation nobody can explain.

InterCo Flow automates the second side. A rule per selling company names the
buying company, the vendor partner to use and the price policy: same price,
source price plus a transfer margin, or the source standard cost. Product
mappings translate the catalogue when the two companies do not share the same
references. Confirming the sales order creates the intercompany transfer, and
one click writes the matching purchase order in the buying company, with the
right partner, the right products and the transfer price already applied.
Both sides keep the link, so the margin of the operation is visible in one
screen.

* One rule per selling company, with target company and vendor partner.
* Price policy: same price, source price plus margin, or source cost.
* Product mapping between the two catalogues.
* Transfer record with sale amount, purchase amount and margin.
* Purchase order created in the target company in one click.
* Origin and link traced on both the sale and the purchase side.
* Cancel and recreate workflow, never two transfers for one order.
* Multi-company rules: each side only reads what belongs to it.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'price': 149.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'sale',
        'purchase',
        'account',
        'stock',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/interco_transfer_0_views.xml',
        'views/interco_transfer_line_1_views.xml',
        'views/interco_rule_2_views.xml',
        'views/interco_mapping_3_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
