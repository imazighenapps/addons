# -*- coding: utf-8 -*-
{
    'name': 'ToolLife',
    'version': '18.0.1.0.0',
    'summary': 'Track tool and die usage cycles against their life limits and plan replacements before they fail in production.',
    'description': '''ToolLife - Tools Replaced In Time
=================================
Track tool and die usage cycles against their life limits and plan replacements before they fail in production.

Key points:
* Tools & dies tracked in a dedicated register.
* Cycle counts recorded with clear ownership and dates.
* Replacement due visible so nothing slips through.
* Draft, confirmed and done states with an audit trail.
* Computed totals and counts kept up to date.
* Active flag to archive records no longer needed.
* Company-aware records for multi-company use.
* Mail chatter for notes and follow-up.''',
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
        'views/tool_life_entry_0_views.xml',
        'views/tool_life_item_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
