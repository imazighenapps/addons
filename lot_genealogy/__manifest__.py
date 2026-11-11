# -*- coding: utf-8 -*-
{
    'name': 'Genealogy',
    'version': '18.0.1.0.0',
    'summary': 'Trace the family tree of every produced lot: which parents fed it and which children inherit a quality issue.',
    'description': '''Genealogy - Every Lot Knows Its Roots
=====================================
When a quality issue hits a produced lot, the first question is simple:
which input lots fed it, and which finished lots inherited the same
risk? The answer usually lives in production notes, spreadsheets and
memory, and tracing it back takes hours while the suspect stock keeps
moving.

Genealogy keeps one record per lot with its product, reference and
production date, and links each lot to the parent lots that fed it and
the child lots produced from it. Parent and child counts are stored on
the lot so you can see at a glance whether a lot is a root, a leaf or
part of a long chain. Marking a lot as impacted flags it for follow-up,
and the ancestry screen lets you walk the tree in both directions.
When the recall question comes, the family tree is already drawn.

* One record per lot with product, reference and production date.
* Parent and child links to trace ancestry in both directions.
* Stored parent and child counts on every lot.
* Impact flag to mark lots affected by a quality issue.
* Ancestry and descendant views to walk the family tree.
* Notes kept on each lot and link for investigation context.
* A clear register of roots, intermediates and leaves.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Inventory',
    'license': 'OPL-1',
    'price': 79.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/lot_genealogy_0_views.xml',
        'views/lot_genealogy_link_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
