# -*- coding: utf-8 -*-
{
    'name': 'FreightWatch',
    'version': '18.0.1.0.0',
    'summary': 'Audit the transport lines on supplier bills against the freight tariffs you negotiated and keep the overcharges.',
    'description': '''FreightWatch - Freight Charged Fairly
=====================================
Transport costs hide inside supplier bills: a fuel surcharge here, a handling
fee there, and the invoice total looks reasonable until someone compares it
to the tariff you negotiated. Overcharges slip through because checking every
freight line by hand takes longer than paying the bill. At month end the
logistics spend is wrong and nobody can prove where it leaked.

FreightWatch keeps the freight tariffs you negotiated and audits every billed
transport line against them. A tariff records the carrier, the lane and the
agreed amount, while each bill line records what the supplier actually
charged. The overcharge is computed and stored on every line, so excess cost
is visible without a spreadsheet. A disputed flag keeps challenged amounts in
one place until the supplier corrects them. An overcharges screen shows every
line billed above tariff instead of buried in invoices. The proof the buyer
needs is the one the module already holds.

* A register of freight tariffs with carrier, lane and agreed amount.
* Bill lines linked to a tariff with the amount actually charged.
* Overcharge computed and stored on every billed line.
* A disputed flag to track challenged freight amounts.
* An overcharges screen for every line billed above tariff.
* States to follow a line from draft to checked and disputed.
* Charged and tariff amounts must stay non-negative.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Purchase/Purchase',
    'license': 'OPL-1',
    'price': 45.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/freight_tariff_0_views.xml',
        'views/freight_bill_line_1_views.xml',
        'views/freight_bill_overcharge_2_views.xml',
        'views/menus.xml',
        'views/freight_bill_overcharge_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
