# -*- coding: utf-8 -*-
{
    'name': 'AnnounceBoard',
    'version': '19.0.1.0.0',
    'summary': 'Publish and manage internal announcements with title, content, audience, publish and expiry dates, and draft/published/archived states in a company-safe board.',
    'description': '''AnnounceBoard - Internal Employee Announcements
===============================================
Important updates sent by email or chat get buried and missed. Teams need one
place to see current company and departmental announcements.

AnnounceBoard provides a simple announcement register. Create notices with a
title, content, target department and validity dates, publish them when ready and
archive them when no longer relevant so employees can focus on current information.

* Announcements with title, rich content, author and department target.
* Publish and expiry dates with priority flag.
* States: draft, published, archived.
* Search and grouping by state, department and period.
* Multi-company, no Enterprise dependency, no external Python package.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Human Resources/Employee',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'hr',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/employee_announcement_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
