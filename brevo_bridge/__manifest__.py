# -*- coding: utf-8 -*-
{
    'name': 'Brevo Bridge',
    'version': '20.0.1.0.0',
    'summary': 'Sync contacts and lists with Brevo, track campaign/event feedback and keep marketing data aligned with your CRM.',
    'description': '''Brevo Bridge - Connect Odoo contacts with Brevo
===============================================
Marketing and sales teams use Brevo for campaigns while contacts and leads
live in Odoo. Manual exports create duplicates, outdated opt-ins and no
visibility on campaign engagement.

Brevo Bridge manages connection settings, contact sync records and audience
lists. Contacts can be prepared and pushed (or pulled in concept) as sync
entries with mapped attributes and consent state. Event logs capture
engagement feedback such as delivered, opened, clicked or bounced so CRM
users can see marketing signals directly in Odoo.

* Brevo connection profile with API key and sender settings.
* Contact sync records linked to partners/leads with status tracking.
* Audience/list definitions and membership counts.
* Campaign/event log for engagement feedback.
* Prepare, sync, and reset actions with error messages.
* Opt-in/consent flag and last sync timestamp.
* No external Python dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Marketing/Email Marketing',
    'license': 'OPL-1',
    'price': 99.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'crm',
        'contacts',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/brevo_connection_0_views.xml',
        'views/brevo_contact_sync_1_views.xml',
        'views/brevo_event_log_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
