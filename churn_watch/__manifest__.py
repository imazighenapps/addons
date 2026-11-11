# -*- coding: utf-8 -*-
{
    'name': 'ChurnWatch',
    'version': '20.0.1.0.0',
    'summary': 'Spot the subscribers and repeat customers who stop ordering and trigger a save action before they are gone.',
    'description': '''ChurnWatch - Nobody Slips Away Twice
====================================
Customers rarely announce that they are leaving: they simply stop
ordering. The last invoice grows older, the account manager notices too
late and the save call happens after the competitor has already won the
next order. Without a shared radar, silence looks the same as loyalty.

ChurnWatch keeps a risk signal per customer with the last order date,
the silence threshold and the computed days without activity. When the
signal is at risk, you log save actions with an owner, a planned date
and an outcome, so the team can see who was contacted and what worked.
Closing a signal records the resolution and keeps the history for the
next review.

* A risk signal per customer with last activity and silence threshold.
* Days without activity computed and stored on each signal.
* Risk status derived from the threshold to focus the save queue.
* Save actions with owner, planned date, outcome and notes.
* One screen for at-risk customers and their follow-up actions.
* Search filters for signals at risk and actions still pending.
* Validation that refuses impossible dates and thresholds.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
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
        'views/churn_signal_0_views.xml',
        'views/churn_action_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
