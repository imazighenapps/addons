# -*- coding: utf-8 -*-
{
    'name': 'YieldWatch',
    'version': '20.0.1.0.0',
    'summary': 'Compare the output a production order should give with what it gave and name the losses that repeat.',
    'description': '''YieldWatch - Losses Never Anonymous
===================================
A production order is planned for one hundred units and closes at
ninety-two. The eight missing pieces disappear into a rounding habit:
one scrap here, one rework there, never the same reason twice on paper
and always the same losses in reality. Without a named record the plant
manager cannot tell whether the yield is drifting, which step eats the
output or how much material the gap really costs.

YieldWatch keeps one Odoo record per production run: the product, the
planned output and the actual output you really obtained. The lost
quantity and the yield rate are computed and stored on the run so every
loss can be filtered and grouped without a spreadsheet. Each run carries
its own loss lines: a named reason, the quantity lost, the step and a
note, so the same cause can be counted across orders instead of guessed.
Closing the run freezes the figures, and the whole story stays in the
chatter for the next review.

* One run record per production order with planned and actual output.
* Lost quantity and yield rate computed and stored on every run.
* Named loss lines with reason, step, quantity and note.
* Counters on the run for loss lines and total lost quantity.
* Draft, running and closed states with an audit trail.
* Closing the run freezes output and losses from further edits.
* A negative or impossible output is refused for you.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
    'license': 'OPL-1',
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/yield_run_0_views.xml',
        'views/yield_loss_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
