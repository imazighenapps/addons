# -*- coding: utf-8 -*-
{
    'name': 'MarginGuard',
    'version': '19.0.1.0.0',
    'summary': 'Set discount and margin floors per product or category and block the sale order line until the rule is respected.',
    'description': '''MarginGuard - No Discount Below The Floor
=========================================
Year end arrives, the rep wants the deal, and the order line goes out
at 35 percent off a product whose category is already sold thin. The
rule was written on a whiteboard in January, by December nobody reads
it, and the invoice shows a beautiful sale with no margin left. When
the finance review asks why that product bled for a quarter, the answer
is nobody saw the discount leave.

MarginGuard holds your floors in one Odoo place: discount floor and
margin floor per product, per category, per customer or for every
line, in percentages anyone can read. Every attempt that goes below a
floor becomes a check with the reference of the line, the discount and
the margin requested, and the decision pending until you say yes.
Approve or refuse from the check itself, with the date and the person
who decided, and the approvals screen lists the checks you still have
to chase. The rule stops living on the whiteboard: it enforces itself.

* Discount and margin floors in percentages, in one place.
* A scope for every rule: product, category, customer or global.
* Every attempt below a floor becomes an explicit check.
* The reference, discount and margin requested on each check.
* Approve or refuse, with the date and the decision maker recorded.
* One screen of the approvals you still have to chase.
* A rule without any floor is refused for you.
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
        'views/margin_rule_0_views.xml',
        'views/margin_check_1_views.xml',
        'views/margin_approvals_2_views.xml',
        'views/menus.xml',
        'views/margin_approvals_action.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
