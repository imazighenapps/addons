# -*- coding: utf-8 -*-
{
    'name': 'ContractRate',
    'version': '19.0.1.0.0',
    'summary': 'Lock negotiated customer prices for a period and flag any quotation that drifts away from the agreed rate card.',
    'description': '''ContractRate - Agreed Rates, Held Firm
======================================
Lock negotiated customer prices for a period and flag any quotation that drifts away from the agreed rate card.

Key points:
* Agreed rates tracked in a dedicated register.
* Validity dates recorded with clear ownership and dates.
* Rate breaches visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
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
        'views/contract_price_entry_0_views.xml',
        'views/contract_price_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
