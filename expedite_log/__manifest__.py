# -*- coding: utf-8 -*-
{
    'name': 'PremiumWatch',
    'version': '20.0.1.0.0',
    'summary': 'Log every expedited or emergency purchase with the extra premium it cost and show who triggered it most.',
    'description': '''PremiumWatch - Urgency Has A Price
==================================
Expedited purchases save a production line today and quietly inflate costs
tomorrow. A rush shipment, an emergency buy, a same-day courier: each one
carries an extra premium that nobody totals because the reason and the cost
stay in separate emails. By the time the spend review arrives, the pattern is
gone and the same teams keep paying for urgency.

PremiumWatch logs every expedited or emergency purchase as one entry: who
requested it, why it was urgent, what it would have cost normally and what it
actually cost. The premium is computed and stored on every entry, so the
extra spend is visible at once. A reason and a requester are kept on the
record, making repeat offenders easy to spot in the grouped view. The entry
moves from draft to confirmed when the cost is known. A high-premium screen
shows the costly emergencies instead of a flat list. The urgency bill the
buyer needs is the one the module already produces.

* A log entry per expedited or emergency purchase.
* Normal cost and actual cost recorded on every entry.
* The urgency premium computed and stored for analysis.
* Requester and reason kept to spot repeat patterns.
* States to follow an entry from draft to confirmed.
* A screen focused on costly premium entries.
* Actual and normal costs must stay non-negative.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Purchase/Purchase',
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
        'views/expedite_entry_0_views.xml',
        'views/expedite_entry_premium_1_views.xml',
        'views/menus.xml',
        'views/expedite_entry_premium_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
