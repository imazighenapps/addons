# -*- coding: utf-8 -*-
{
    'name': 'RequisitionBook',
    'version': '20.0.1.0.0',
    'summary': 'Collect purchase requisitions from teams, approve them and convert approved needs into purchase orders.',
    'description': '''RequisitionBook - Needs Raised, Orders Placed
=============================================
Collect purchase requisitions from teams, approve them and convert approved needs into purchase orders.

Key points:
* Requisitions tracked in a dedicated register.
* Approval flow recorded with clear ownership and dates.
* PO conversion visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
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
        'security/ir.access.csv',
        'views/purchase_requisition_entry_0_views.xml',
        'views/purchase_requisition_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
