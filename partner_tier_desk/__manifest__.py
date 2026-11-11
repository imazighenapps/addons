# -*- coding: utf-8 -*-
{
    'name': 'PartnerTier',
    'version': '19.0.1.0.0',
    'summary': 'Run a reseller or referral partner program with tiers, targets and the benefits each level unlocks.',
    'description': '''PartnerTier - Partners Who Grow With You
========================================
Run a reseller or referral partner program with tiers, targets and the benefits each level unlocks.

Key points:
* Reseller tiers tracked in a dedicated register.
* Tier targets recorded with clear ownership and dates.
* Tier benefits visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'CRM/CRM',
    'license': 'OPL-1',
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/partner_tier_entry_0_views.xml',
        'views/partner_tier_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
