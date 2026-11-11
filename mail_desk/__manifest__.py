# -*- coding: utf-8 -*-
{
    'name': 'MailDesk',
    'version': '18.0.1.0.0',
    'summary': 'Log the registered and tracked mail that enters or leaves the company and who collected each item.',
    'description': '''MailDesk - Mail In, Mail Out, Traced
====================================
Registered letters and parcels arrive at reception, get signed for on
a paper log and wait on a shelf until someone remembers to collect
them. Outbound tracked mail leaves with no central record of the
tracking number or the day it was sent. When a customer asks for proof
of dispatch or a colleague looks for a registered letter, the answer is
a notebook.

MailDesk keeps one Odoo record per registered or tracked item: inbound
or outbound, sender or recipient, tracking number and the date it was
logged. When the item is collected or delivered, the pickup is stamped
with who collected it and when. A pickup screen shows everything still
waiting, so nothing sits on the shelf unnoticed.

* A register of inbound and outbound tracked mail items.
* Sender or recipient, tracking number and logged date on each item.
* The collector and pickup date stamped when the item is collected.
* A clear state from waiting to collected.
* One pickup screen for everything still waiting.
* A pickup before the logged date is refused for you.
* Chatter traceability on every mail record.
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
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/mail_item_0_views.xml',
        'views/mail_waiting_1_views.xml',
        'views/menus.xml',
        'views/mail_waiting_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
