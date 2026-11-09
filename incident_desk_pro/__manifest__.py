# -*- coding: utf-8 -*-
{
    'name': 'IncidentDesk',
    'version': '19.0.1.0.0',
    'summary': 'Log workplace, property and environment incidents with a severity, drive the investigation in Odoo and close each case only when every corrective action is done.',
    'description': '''IncidentDesk - Every Incident Corrected For Real
================================================
An incident arrives in a mailbox, is discussed in a meeting, and the
corrective actions promised there are never tracked. The same pallet
falls three times before somebody can prove nothing was ever closed,
and the file that the safety auditor asks for does not exist.

IncidentDesk gives every workplace event one Odoo record: injury, near
miss, property damage, environment or other, with a severity and the
exact location. Reporting takes a minute; the workflow takes over -
investigation, corrective and preventive actions owned by users with due
dates, and a closing gate that refuses to mark the incident closed
while one action is still open. Reopening is one click and leaves a
dated trail, so the file shows what was really done and when.

* Incidents typed as injury, near miss, property, environment or other.
* Severity from low to critical, with the location.
* Draft, investigating and closed states with a chatter trail.
* Corrective and preventive actions with owner and due date.
* No closing while one corrective action is still open.
* One company-wide screen for every action still to do.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Operations/Operations',
    'license': 'OPL-1',
    'price': 89.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/ehs_incident_0_views.xml',
        'views/ehs_action_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
