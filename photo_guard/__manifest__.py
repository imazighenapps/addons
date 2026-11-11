# -*- coding: utf-8 -*-
{
    'name': 'PhotoGuard',
    'version': '20.0.1.0.0',
    'summary': 'Find every product that ships without a proper picture and fix the catalog before the webstore does it for you.',
    'description': '''PhotoGuard - A Catalog Ready To Show
====================================
Product catalogs go live with missing or outdated pictures: the webstore
shows placeholders, sales teams send the wrong image, and nobody owns a
clear list of what must be fixed. Audits happen in spreadsheets and the
same gaps reappear after every import.

PhotoGuard gives you photo audits in Odoo that list every product issue in
one place. Each audit records the target catalog area, its due date and the
reviewed lines with the missing or weak photo status, and computes open and
fixed counts as the work progresses. Issues move from open to fixed, audits
can be completed when nothing is left open, and marking a fixed issue again
is refused. The catalog you publish is the one the audit already cleared.

* Photo audits with a target area, owner and due date.
* Issue lines per product with missing, weak or outdated status.
* A simple issue workflow from open to fixed.
* Open and fixed counters computed and stored on each audit.
* Audits that can be completed only when every issue is fixed.
* Fixing an issue twice is refused for you.
* A quality score computed from the fixed issues.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'price': 29.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/photo_audit_0_views.xml',
        'views/photo_issue_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
