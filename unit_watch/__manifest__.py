# -*- coding: utf-8 -*-
{
    'name': 'UnitWatch',
    'version': '19.0.1.0.0',
    'summary': 'Catch the kg/lb, litre/cl and unit slips that slip into orders, receipts and bills before they cost money.',
    'description': '''UnitWatch - No Unit Slips Through
=================================
A quantity typed in kilograms instead of grams, a litre confused with a
centilitre, or a unit mistaken for a box: small unit slips pass through
orders, receipts and bills unnoticed and turn into expensive surprises
when the stock count or the invoice arrives. The mistake is obvious in
hindsight, but nobody has a simple place to record and review it.

UnitWatch keeps a register of unit checks: the document reference, the
product, the expected unit, the entered unit and the quantity that
looked suspicious. Each check is classified by source and severity, and
a stored suspicious flag highlights the lines that still need attention.
When the line is corrected you record the right quantity and close the
check, keeping the original values for the audit trail. The suspicious
queue shows every open slip so corrections happen before money moves.

* A register of unit checks with document, product and source.
* Expected and entered units with the suspicious quantity.
* Severity and source classification for every check.
* Stored suspicious flag for lines that still need attention.
* Correction fields to record the right quantity and close the check.
* Original values kept for a clear audit trail.
* A suspicious queue to review open slips in one screen.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Inventory/Inventory',
    'license': 'OPL-1',
    'price': 29.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/unit_check_0_views.xml',
        'views/unit_suspicious_1_views.xml',
        'views/menus.xml',
        'data/ir_sequence_data.xml',
        'views/unit_suspicious_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
