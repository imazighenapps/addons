# -*- coding: utf-8 -*-
{
    'name': 'RecallDesk',
    'version': '18.0.1.0.0',
    'summary': 'When a lot must be recalled, list in one click every customer who received it and produce the recall letters.',
    'description': '''RecallDesk - One Recall, One Click
==================================
When a defective lot is discovered, the recall starts in panic: who
received it, which delivery, which quantity and which customer must be
called first. The information is scattered across deliveries, emails
and spreadsheets, and every hour lost increases the risk and the cost
of the recall.

RecallDesk turns each recall into a single Odoo case with the recalled
product, the reason, the start date and a clear status. Impact lines
record every affected lot, customer, quantity and delivery reference so
the recall scope is explicit and reviewable. You can move the case from
draft to active, mark customers as notified and close the recall only
when every impacted line is handled. The recall scope, the decisions
and the communication trail stay on one record.

* A recall case per incident with product, reason and start date.
* Impact lines for affected lot, customer, quantity and reference.
* Stored totals for impacted lines and notified customers.
* A workflow from draft to active, notifying, closed and cancelled.
* One-click actions to mark all impacted customers as notified.
* A dedicated screen for open recalls and pending notifications.
* Closing is refused while impacted customers remain unnotified.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Inventory',
    'license': 'OPL-1',
    'price': 99.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/lot_recall_0_views.xml',
        'views/lot_recall_line_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
