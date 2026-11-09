# -*- coding: utf-8 -*-
{
    'name': 'TargetPilot',
    'version': '18.0.1.0.0',
    'summary': 'Set monthly or quarterly targets per salesperson and team, compute the confirmed revenue achieved, and show the gap, the pace and the projected end of period.',
    'description': '''TargetPilot - Sales Targets and Achievement
===========================================
The kickoff meeting announces the quarterly target. The number is written on
a slide, and then nothing tracks it: the pipeline report shows the pipeline,
the revenue report shows history, and the only place where the two meet is
the monthly spreadsheet somebody updates by hand.

TargetPilot gives the number a record of its own. One target per salesperson
and one per team says when the period runs and what has to be invoiced. The
module computes the confirmed revenue on that window, keeps the gap in
currency, converts it to a percentage, and returns the projection for the
end of period from the current pace. The record keeps a state, so a target
can be opened, achieved and closed, and a duplicate definition is refused.

* Dated window per target, monthly or quarterly.
* Owner is the salesperson, with the team on top.
* Achievement is the confirmed revenue of the window.
* Gap and percentage computed, stored and history-proof.
* Pace and end of period projection on the record.
* Draft, running, done states, one click per step.
* Target of the same owner twice in the same window refused.
* Company isolation, group by owner and state.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'price': 109.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'sale',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/sales_target_0_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
