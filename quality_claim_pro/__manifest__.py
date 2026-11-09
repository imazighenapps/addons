# -*- coding: utf-8 -*-
{
    'name': 'ClaimDesk',
    'version': '19.0.1.0.0',
    'summary': 'Register every quality claim with its product, lot, quantity and root cause, run a short eight-step resolution, and keep the cost and the corrective actions on one record.',
    'description': '''ClaimDesk - Customer and Supplier Claims
========================================
A customer returns a batch that does not fit. The warehouse opens a
spreadsheet, the quality team opens a second one, the corrective actions
live in a mailbox, and nobody ever adds up what the claim really cost.

ClaimDesk keeps one record per claim, whatever its origin: a customer
complaint, a supplier defect or an internal non-conformity. The claim
carries the partner, the product, the lot reference, the quantity and a
defect code, so the same story is told the same way by everybody. The
severity and the cost amount turn a pile of complaints into a list that
can be sorted and arbitrated.

From there the record follows a short, guided workflow. Opening the claim
starts the analysis; investigating moves it to the quality engineer; a
root cause is mandatory before corrective actions can be planned. Each
corrective action has a responsible user and a due date, and the claim
cannot be closed while one of them is still open. The whole trail stays
in the chatter.

* Customer, supplier and internal quality claims.
* Product, lot reference, quantity and defect code.
* Severity from minor to critical, with the monetary cost of the claim.
* Draft, open, investigation, action, done and refused states.
* A root cause required before corrective actions are planned.
* Dated corrective actions with a responsible user.
* Closing refused while a corrective action is still open.
* Kanban, graph and chatter, multi-company isolation.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Manufacturing/Manufacturing',
    'license': 'OPL-1',
    'price': 119.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'product',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/quality_claim_0_views.xml',
        'views/quality_claim_action_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
