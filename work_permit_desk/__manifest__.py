# -*- coding: utf-8 -*-
{
    'name': 'WorkPermit',
    'version': '18.0.1.0.0',
    'summary': 'Authorise each contractor intervention on site with a dated work permit and a validity the reception checks.',
    'description': '''WorkPermit - Permits Before Tools
=================================
A contractor shows up at the gate with a van full of tools and a verbal
"go ahead" from someone who is not on site. Reception has no way to tell
whether the intervention is authorised, for which zone, and until when.
Hot work, electrical jobs and confined spaces all happen under the same
uncertainty, and the permit that should have been signed is a sheet lost
in an inbox.

WorkPermit issues a dated work permit in Odoo for every contractor
intervention. Each permit names the contractor, the site area, the work
description and the period it is valid, and it moves from draft to
authorised before anyone starts. The reception desk can see which permits
are valid right now and which have expired, and closing a permit stamps
the time the intervention ended. Expired or unauthorised work is no
longer a matter of memory because the permit is the answer.

* A register of contractor work permits with site area and scope.
* Validity period with start and end dates checked at the gate.
* Authorisation workflow before work can begin.
* A close action that stamps when the intervention ended.
* Active and expired permits visible in one screen.
* One register for every contractor intervention on site.
* An end date before the start date is refused for you.
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
        'views/work_permit_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
