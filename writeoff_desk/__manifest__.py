# -*- coding: utf-8 -*-
{
    'name': 'WriteOffBook',
    'version': '18.0.1.0.0',
    'summary': 'Request, approve and post bad-debt or small-balance write-offs with a reason and a clear audit trail.',
    'description': '''WriteOffBook - Write-Offs, Properly Approved
============================================
Request, approve and post bad-debt or small-balance write-offs with a reason and a clear audit trail.

Key points:
* Write-off requests tracked in a dedicated register.
* Approvals recorded with clear ownership and dates.
* Written-off amounts visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
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
        'views/writeoff_desk_entry_0_views.xml',
        'views/writeoff_desk_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
