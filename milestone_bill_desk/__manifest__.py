# -*- coding: utf-8 -*-
{
    'name': 'MilestoneBill',
    'version': '19.0.1.0.0',
    'summary': 'Tie invoicing to project milestones so you bill what was delivered and never miss a billable event.',
    'description': '''MilestoneBill - Bill What Was Delivered
=======================================
Tie invoicing to project milestones so you bill what was delivered and never miss a billable event.

Key points:
* Milestones tracked in a dedicated register.
* Billable events recorded with clear ownership and dates.
* Invoiced milestones visible so nothing slips through.
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
    'price': 69.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/milestone_bill_entry_0_views.xml',
        'views/milestone_bill_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
