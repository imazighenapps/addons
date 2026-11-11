# -*- coding: utf-8 -*-
{
    'name': 'QuoteRevise',
    'version': '18.0.1.0.0',
    'summary': 'Turn every change to a confirmed quotation into a dated revision, so the approved version is never silently edited.',
    'description': '''QuoteRevise - Approved Versions Only
====================================
A confirmed quotation starts moving: the price moves, the quantity
drifts, the delivery date slides by a week. On the Odoo side the record
was never touched in an obvious way, and the copy you sent by email no
longer matches anything. When the customer disputes the amount, nobody
can say which version they approved or who agreed to it.

QuoteRevise keeps every change to a quotation as an explicit amendment:
one line per quotation with its revision number, the reason for the
change and the list of what it modifies, with the previous value and
the new value side by side. The amendment has to be submitted and then
approved, and approval stamps the date and the person who sealed the
version. The compare screen shows old and new next to each other, and
the approved screen shows the exact version your customer signed off
on. Trail, dates, decision: everything the disputed order will need is
already in the record.

* An explicit amendment for every change to a quotation.
* A revision number per version, always above zero.
* Old value and new value side by side for every change.
* A reason archived with the amendment.
* Submit then approve, with the approval date and approver recorded.
* One compare screen of old and new values next to each other.
* One approved-versions screen of what the customer agreed to.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/quote_amendment_0_views.xml',
        'views/quote_compare_1_views.xml',
        'views/quote_approved_2_views.xml',
        'views/menus.xml',
        'views/quote_approved_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
