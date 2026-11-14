# -*- coding: utf-8 -*-
{
    'name': 'Teams Notifications',
    'version': '18.0.1.0.0',
    'summary': 'Configure Microsoft Teams webhooks and notification rules to push Odoo business alerts to channels.',
    'description': '''Teams Notifications - Send Odoo alerts to Microsoft Teams
=========================================================
Teams keep teams aligned, but important Odoo events (orders, invoices,
approvals, stock alerts) often stay inside Odoo. Teams Notifications lets
you define incoming webhooks and rules that generate notification records
and formatted messages for Teams channels.

* Webhook/channel configuration per company.
* Notification rules by model/event type and conditions text.
* Notification records with status and payload preview.
* Send/test actions and delivery log.
* No external Python dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Productivity/Discuss',
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
        'views/teams_channel_0_views.xml',
        'views/teams_notification_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
