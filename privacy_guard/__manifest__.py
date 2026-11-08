# -*- coding: utf-8 -*-
{
    'name': 'PrivacyGuard',
    'version': '20.0.1.0.0',
    'summary': 'Set retention periods per model, anonymize sensitive fields, and handle access and erasure requests with dated, auditable proof.',
    'description': '''PrivacyGuard - GDPR Retention and Erasure
=========================================
GDPR does not ask you to keep everything forever: it asks you to keep
personal data only as long as needed, and to answer every data subject
request on time.

PrivacyGuard turns those two obligations into a routine. Declare one
retention rule per model: the date field that measures the age of a
record, the number of days to keep it, and what to do once it is
expired. Anonymization is defined field by field, with the mask you
choose. A scan screen counts what is expired and applies the actions
only when you ask for it. Every data subject request - access, erasure,
rectification, portability - is tracked with a 30-day legal deadline and
a full history of who did what, so the proof is always one click away.

* Retention policy per model: date field, retention days and action.
* Field-by-field anonymization with a configurable mask character.
* Archive or delete expired data, with a safe dry-run scan first.
* Data subject requests: access, erasure, rectification, portability.
* A 30-day legal deadline computed from the request date.
* A processing register keeping every rule and every request on record.
* Partners are never deleted: erasure masks their personal data.
* Multi-company, traced in the chatter, no Enterprise dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Tools/Privacy',
    'license': 'OPL-1',
    'price': 99.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'contacts',
    ],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'views/privacy_rule_0_views.xml',
        'views/privacy_request_1_views.xml',
        'views/privacy_scan_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
