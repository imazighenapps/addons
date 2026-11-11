# -*- coding: utf-8 -*-
{
    'name': 'PatrolBook',
    'version': '20.0.1.0.0',
    'summary': 'Record the security patrol rounds and their findings, and expose the checkpoints that were skipped.',
    'description': '''PatrolBook - Rounds You Can Prove
=================================
A guard walks the site at night, ticks boxes on a clipboard and the
morning shift inherits a story nobody can verify. When a gate is found
open or a camera is offline, the question is always the same: was that
checkpoint visited at all, and what was seen there. Skipped stops hide
inside a paper round, and the proof a client or an insurer asks for does
not exist.

PatrolBook records every patrol round in Odoo with its guard, its route
and the time it started and finished. Each checkpoint is logged as a stop
with a status, the observation made on site and the time it was checked,
so skipped points stand out instead of disappearing. Findings can be
flagged on a stop and the round keeps a computed count of what was missed
and what needs attention. The register of rounds is the proof the next
shift, the client and the auditor can all read.

* A register of patrol rounds with guard, route and schedule.
* Stops per round with checkpoint, status and observation.
* The time each checkpoint was checked, stored on the stop.
* Skipped checkpoints exposed and counted on the round.
* Findings flagged on a stop for quick follow-up.
* A single screen to review rounds and their stops.
* A stop time before the round start is refused for you.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
    'license': 'OPL-1',
    'price': 39.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/patrol_round_0_views.xml',
        'views/patrol_stop_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
