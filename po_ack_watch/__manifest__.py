# -*- coding: utf-8 -*-
{
    'name': 'AckWatch',
    'version': '20.0.1.0.0',
    'summary': 'Track which supplier confirmed which purchase order and chase the acknowledgements you are still waiting for.',
    'description': '''AckWatch - Signed By The Supplier
=================================
A purchase order sent to a supplier is not a commitment until it is
acknowledged, yet the confirmation often lives in a mailbox nobody
shares. Buyers resend the same request, planners assume the delivery is
secured and late acknowledgements surface only when the dock is empty.
There is no single view of what is confirmed and what is still pending.

AckWatch keeps a record per purchase order with the supplier, the sent
date and the acknowledgement deadline. When the supplier confirms, the
record stores who acknowledged it and on which date. Follow-up notes
trace every chase sent to the supplier, while the unacknowledged view
lists the orders that are still waiting so the buyer knows exactly what
to chase.

* A tracking record per purchase order with supplier and references.
* Sent date, acknowledgement deadline and confirmed acknowledgement date.
* Acknowledge action that stamps the supplier confirmation details.
* Follow-up notes to log every chase sent to the supplier.
* Computed counters for follow-ups and days waiting stored on the record.
* Search filters for unacknowledged and overdue purchase orders.
* Validation that refuses impossible dates and duplicate acknowledgements.
* Multi-company isolation out of the box.''',
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
        'views/po_ack_order_0_views.xml',
        'views/po_ack_followup_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
