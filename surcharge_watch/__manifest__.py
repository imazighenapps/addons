# -*- coding: utf-8 -*-
{
    'name': 'Surcharge',
    'version': '18.0.1.0.0',
    'summary': 'Recompute the raw material surcharge your suppliers may bill from the index you agreed and flag the deltas.',
    'description': '''Surcharge - Indexes Applied Right
=================================
Suppliers bill raw material surcharges from commodity indexes, but the
formula lives in a contract clause and the recomputation happens in a
spreadsheet. When the index moves, invoices arrive with rounded or
outdated surcharges and nobody can prove which value was correct on the
billing date.

Surcharge keeps every index clause in Odoo with its base index, its
factor and the supplier it applies to. Each applied surcharge records
the billing period, the current index, the computed amount and the
amount actually billed, so the delta is stored and visible. You can
review variances before paying, mark a line as accepted or disputed and
keep a dated explanation in chatter. The agreed formula and the billed
reality live on the same record.

* Index clauses with supplier, base index and surcharge factor.
* Applied surcharge lines per billing period and clause.
* The expected surcharge computed and stored from the index values.
* The billed amount compared with a stored variance.
* A clear workflow to review, accept or dispute each surcharge.
* One screen for clauses and one for billed surcharge variances.
* Disputes require no silent edits to the agreed formula.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Purchase/Purchase',
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
        'views/surcharge_clause_0_views.xml',
        'views/surcharge_line_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
