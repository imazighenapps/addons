# -*- coding: utf-8 -*-
{
    'name': 'LabWatch',
    'version': '20.0.1.0.0',
    'summary': 'Send samples to the external lab with a barcoded request and get the results back where the lot can see them.',
    'description': '''LabWatch - Results Back To The Lot
==================================
Samples leave for the external lab with a paper slip, an email thread
and a promise to call back: the request number lives in someone's
inbox, the lot on the floor waits without news and the result arrives
as a PDF nobody can find when the release decision is due. When a
customer asks which analysis cleared a lot, the trail is a folder of
attachments.

LabWatch keeps one Odoo request per sample: the lot reference, the
barcode, the external laboratory and the date it was sent. When the
result comes back, it is recorded on the same request with the outcome
and the date received, so the lot can see it immediately. An awaiting
screen shows every sample still at the lab, and nothing is closed
until the result is filed.

* A sample request with lot reference and barcoded identifier.
* The external laboratory and the date the sample was sent.
* The result and outcome recorded when the analysis comes back.
* A clear state from sent to result received.
* One awaiting screen for samples still at the lab.
* A received date before the sent date is refused for you.
* Chatter traceability on every sample request.
* Multi-company isolation out of the box.''',
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
        'security/ir.access.csv',
        'views/lab_sample_0_views.xml',
        'views/lab_awaiting_1_views.xml',
        'views/menus.xml',
        'views/lab_awaiting_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
