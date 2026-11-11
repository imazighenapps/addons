# -*- coding: utf-8 -*-
{
    'name': 'CampaignROI',
    'version': '19.0.1.0.0',
    'summary': 'Track spend and attributed revenue per campaign and see which actions really pay back and which do not.',
    'description': '''CampaignROI - Spend That Proves Itself
======================================
Track spend and attributed revenue per campaign and see which actions really pay back and which do not.

Key points:
* Campaign spend tracked in a dedicated register.
* Attributed revenue recorded with clear ownership and dates.
* ROI by campaign visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Marketing/Marketing',
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
        'views/campaign_roi_entry_0_views.xml',
        'views/campaign_roi_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
