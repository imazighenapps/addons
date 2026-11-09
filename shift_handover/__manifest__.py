# -*- coding: utf-8 -*-
{
    'name': 'ShiftHandover',
    'version': '19.0.1.0.0',
    'summary': 'A dated handover book for every shift: open incidents, pending tasks, stock and quality points, with an owner, a severity and a follow-up flag for the next team.',
    'description': '''ShiftHandover - Nothing Lost Between Shifts
===========================================
The night team patches a leaking valve at four in the morning and goes home.
The morning team walks in, sees a wet floor, and knows nothing: who was
called, which supplier is expected at ten, which pallet is still blocked.

ShiftHandover is the notebook every shift writes before it leaves. One
handover per date and per shift, with the employee handing over and the
department it concerns. Each item is typed as incident, task, stock, quality
or other, carries a severity and, when the next team has to act on it, a
follow-up flag. Resolving an item stamps the exact moment it was dealt with;
reopening it clears the stamp, so the list of open points is always the truth
and never a memory. The handover counts its own open items, moves from draft
to done when the shift closes, and can be reopened or cancelled with an audit
trail in the chatter.

* One handover per date, per shift and per responsible employee.
* Items typed as incident, task, stock, quality or other.
* Severity and follow-up flag on every item.
* Resolve and reopen an item with a timestamped resolution.
* Live open-item counter on the handover.
* Draft, done and cancelled states with a chatter trail.
* Handovers and items browsable by shift, status, responsible and category.
* Multi-company isolation, no Enterprise dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
    'license': 'OPL-1',
    'price': 89.0,
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
        'views/shift_handover_0_views.xml',
        'views/shift_handover_line_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
