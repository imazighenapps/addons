# -*- coding: utf-8 -*-
{
    'name': 'TimeApprove',
    'version': '19.0.1.0.0',
    'summary': 'Collect weekly timesheets, route them for approval and lock periods so billed hours stay trustworthy.',
    'description': '''TimeApprove - Hours Approved, Hours Trusted
===========================================
Collect weekly timesheets, route them for approval and lock periods so billed hours stay trustworthy.

Key points:
* Submitted timesheets tracked in a dedicated register.
* Approval queue recorded with clear ownership and dates.
* Locked periods visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Services/Project',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/timesheet_approve_entry_0_views.xml',
        'views/timesheet_approve_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
